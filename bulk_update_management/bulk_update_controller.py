import json
from bulk_update_management.bulk_update_helper import model_names, model_names_with_get_parent_functions, \
    model_serializers, parse_instance_ids, generate_execl_file, convert_many_to_many_fields_to_list, \
    bulk_create_objects
from utils.helper import *
import io
from utils.helper import upload_to_s3
from copy import deepcopy
import xlwt
from django.http import FileResponse
import pandas as pd
from utils.response_messages import *


# Create your views here.
class BulkUpdateController:
    def update(self, request):
        feature = get_query_param(request, "feature", None)
        if not feature:
            return create_response({}, FEATURE_NOT_PROVIDED, status_code=400)
        if "id" not in request.data:
            return create_response({}, ID_NOT_PROVIDED, 404)
        ids = request.data.pop("id")
        if feature.startswith("/"):
            feature = feature.replace("/", "", 1)
        data = {key: value for key, value in request.data.items() if value != ""}
        tbl = model_names[feature]
        if feature == "user":
            instances = tbl.objects.filter(guid__in=ids)
        else:
            instances = tbl.objects.filter(id__in=ids)

        if not instances:
            return create_response({}, NOT_FOUND, 404)
        instances.update(**data)
        if "is_active" in request.data:
            for instane in instances:
                change_related_objects_status(instane, param=request.data.get("is_active"))
        return create_response({}, SUCCESSFUL, 200)


class BulkImportController:
    def create(self, request):
        try:
            feature = get_query_param(request, "feature", None)
            if not feature:
                return create_response({}, FEATURE_NOT_PROVIDED, status_code=400)
            if feature.startswith("/"):
                feature = feature.replace("/", "", 1)
            tbl = model_names[feature]
            serializer = model_serializers[feature]
            model_fields = tbl._meta.get_fields(include_hidden=True)
            fields = [field.name for field in model_fields if not field.auto_created]
            fields_to_remove = ["is_deleted", "created_at", "updated_at", "deleted_at", "is_active", "id"]
            fields = [field for field in fields if field not in fields_to_remove]
            get_foreignkeys = model_names_with_get_parent_functions[feature]
            valid_instances = []
            invalid_instances = []
            for data in request.data:
                raw_data = deepcopy(data)
                response_data = get_foreignkeys(data)
                response_data = convert_many_to_many_fields_to_list(response_data, model_fields)
                initial_data = deepcopy(response_data)
                data_for_serialization = parse_instance_ids(response_data)
                serialized_data = serializer(data=data_for_serialization)
                if serialized_data.is_valid():
                    valid_instances.append(initial_data)
                else:
                    raw_data["error"] = get_first_error_message_from_serializer_errors(serialized_data.errors,
                                                                                       UNSUCCESSFUL)
                    print(raw_data["error"])
                    invalid_instances.append(raw_data)
            created_instances = bulk_create_objects(tbl, valid_instances)
            if not invalid_instances:
                return create_response({}, SUCCESSFUL, status_code=200)
            else:
                excel_file = generate_execl_file(list(invalid_instances[0].keys()), invalid_instances, feature)
                filename = feature.split("/")[-1] + "_rejected_records.xls"
                url = upload_to_s3(excel_file, filename=filename)
                response = {
                    "url": url
                }
                return create_response(response, str(len(invalid_instances)) + " " + RECORDS_NOT_UPLOADED,
                                       status_code=400)
        except Exception as e:
            print(e)
            return create_response({}, UNSUCCESSFUL, status_code=400)


class ExcelPreviewController:
    def preview(self, request):
        feature = get_query_param(request, "feature", None)
        if not feature:
            return create_response({}, FEATURE_NOT_PROVIDED, status_code=400)
        if feature.startswith("/"):
            feature = feature.replace("/", "", 1)
        tbl = model_names[feature]
        fields = [field.name for field in tbl._meta.fields]
        fields_to_remove = ["is_deleted", "created_at", "updated_at", "deleted_at", "is_active", "id"]
        fields = [field for field in fields if field not in fields_to_remove]
        if not request.FILES:
            return create_response({}, INVALID_FILE_FORMAT, status_code=400)
        if not request.FILES.get("file").name.endswith(".xls"):
            return create_response({}, INVALID_FILE_FORMAT, status_code=400)
        file = request.FILES.get('file')
        data = pd.read_excel(file)
        json_data = json.loads(data.to_json(orient="records"))
        imported_data_keys = json_data[0].keys()
        difference = list(set(fields).difference(set(list(imported_data_keys))))
        if difference:
            return create_response({}, INCORRECT_FILE_UPLOADED, 400)

        return create_response(json_data, SUCCESSFUL, status_code=200)


class GetTemplateController:
    def template(self, request):
        try:
            feature = get_query_param(request, "feature", None)
            if not feature:
                return create_response({}, FEATURE_NOT_PROVIDED, status_code=400)
            if feature.startswith("/"):
                feature = feature.replace("/", "", 1)
            tbl = model_names[feature]
            filename = feature.split("/")[-1] + "_import_template"

            buffer = io.BytesIO()
            wb = xlwt.Workbook(encoding="utf-8")
            ws = wb.add_sheet(filename)
            fields = tbl._meta.get_fields(include_hidden=True)
            fields = [field.name for field in fields if not field.auto_created]
            fields_to_remove = ["is_deleted", "created_at", "updated_at", "deleted_at", "is_active", "id"]
            fields = [field for field in fields if field not in fields_to_remove]

            # Sheet header, first row
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num = 0
            for col_num in range(len(fields)):
                row_num += 1
                ws.write(0, col_num, fields[col_num], font_style)

            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=filename + ".xls"
            )
        except Exception as e:
            print(e)
