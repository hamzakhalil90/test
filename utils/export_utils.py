import io

import xlwt
from django.http import FileResponse


class ExportUtility:
    def export_department_data(self, serialized_asset, columns, export_name):
        try:
            buffer = io.BytesIO()
            wb = xlwt.Workbook(encoding="utf-8")
            ws = wb.add_sheet(export_name)
            # Sheet header, first row
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num = 0
            for col_num in range(len(columns)):
                row_num += 1
                ws.write(0, col_num, columns[col_num], font_style)
                # Sheet body, remaining rows
            count = 0
            font_style = xlwt.XFStyle()
            y = 1
            for row in serialized_asset.data:
                ws.write(count + y, 0, str(row["name"]), font_style)
                ws.write(count + y, 1, str(row["details"]), font_style)
                ws.write(count + y, 2, str(row["category"]), font_style)
                ws.write(count + y, 3, str(row["created_at"]), font_style)
                y = y + 1
            count += 1
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=export_name + ".xls"
            )
        except Exception as e:
            print("DEPARTMENT EXCEL EXPORT EXCEPTION", e)

    def export_user_group_data(self, serialized_asset, columns, export_name):
        try:
            buffer = io.BytesIO()
            wb = xlwt.Workbook(encoding="utf-8")
            ws = wb.add_sheet(export_name)
            # Sheet header, first row
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num = 0
            for col_num in range(len(columns)):
                row_num += 1
                ws.write(0, col_num, columns[col_num], font_style)
                # Sheet body, remaining rows
            count = 0
            font_style = xlwt.XFStyle()
            y = 1
            for row in serialized_asset.data:
                ws.write(count + y, 0, str(row["name"]), font_style)
                ws.write(count + y, 1, str(len(row["users"])), font_style)
                y = y + 1
            count += 1
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=export_name + ".xls"
            )
        except Exception as e:
            print("USER GROUP EXCEL EXPORT EXCEPTION", e)

    def export_designation_data(self, serialized_asset, columns, export_name):
        try:
            buffer = io.BytesIO()
            wb = xlwt.Workbook(encoding="utf-8")
            ws = wb.add_sheet(export_name)
            # Sheet header, first row
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num = 0
            for col_num in range(len(columns)):
                row_num += 1
                ws.write(0, col_num, columns[col_num], font_style)
                # Sheet body, remaining rows
            count = 0
            font_style = xlwt.XFStyle()
            y = 1
            for row in serialized_asset.data:
                ws.write(count + y, 0, str(row["name"]), font_style)
                ws.write(count + y, 1, str(row["details"]), font_style)
                ws.write(count + y, 2, str(row["department"]["name"]), font_style)
                ws.write(count + y, 3, str(row["created_at"]), font_style)
                y = y + 1
            count += 1
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=export_name + ".xls"
            )
        except Exception as e:
            print("DESIGNATION EXCEL EXPORT EXCEPTION", e)

    def export_employee_data(self, serialized_asset, columns, export_name):
        try:
            buffer = io.BytesIO()
            wb = xlwt.Workbook(encoding="utf-8")
            ws = wb.add_sheet(export_name)
            # Sheet header, first row
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num = 0
            for col_num in range(len(columns)):
                row_num += 1
                ws.write(0, col_num, columns[col_num], font_style)
                # Sheet body, remaining rows
            count = 0
            font_style = xlwt.XFStyle()
            y = 1
            for row in serialized_asset.data:
                ws.write(
                    count + y,
                    0,
                    str(
                        row["first_name"] + " " + row["last_name"]
                        if row["last_name"]
                        else ""
                    ),
                    font_style,
                )
                ws.write(count + y, 1, str(row["date_of_birth"]), font_style)
                ws.write(count + y, 2, str(row["email"]), font_style)
                ws.write(count + y, 3, str(row["gender"]), font_style)
                ws.write(count + y, 4, str(row["contact_number"]), font_style)
                ws.write(count + y, 5, str(row["emergency_contact_number"]), font_style)
                ws.write(count + y, 6, str(row["emergency_contact_name"]), font_style)
                ws.write(count + y, 7, str(row["address"]), font_style)
                ws.write(count + y, 8, str(row["date_of_joining"]), font_style)
                ws.write(count + y, 9, str(row["sap_id"]), font_style)
                ws.write(count + y, 10, str(row["department"]["name"]), font_style)
                ws.write(count + y, 11, str(row["designation"]["name"]), font_style)
                ws.write(count + y, 12, str(
                    row["grade"]["prefix"] + " " + row["grade"]["number"]
                    if row["grade"]["prefix"]
                    else ""
                ), font_style)
                ws.write(count + y, 13, str(row["created_at"]), font_style)
                ws.write(count + y, 14, str(row["subzone"]["name"]), font_style)  # country here
                ws.write(count + y, 15, str(row["zone"]["name"]), font_style)
                ws.write(count + y, 16, str(row["city"]["name"]), font_style)
                ws.write(count + y, 17, str(row["region"]["name"]), font_style)
                ws.write(count + y, 18, str(row["region"]['country']["name"]), font_style)
                ws.write(count + y, 19, str(row["reports_to"]["first_name"] + " " + row["reports_to"]["last_name"]),
                         font_style)
                ws.write(count + y, 20, str(row["start_time"]), font_style)
                ws.write(count + y, 21, str(row["end_time"]), font_style)
                y = y + 1
            count += 1
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=export_name + ".xls"
            )
        except Exception as e:
            print("Employee EXCEL EXPORT EXCEPTION", e)

    def export_user_data(self, serialized_asset, columns, export_name):
        try:
            buffer = io.BytesIO()
            wb = xlwt.Workbook(encoding="utf-8")
            ws = wb.add_sheet(export_name)
            # Sheet header, first row
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num = 0
            for col_num in range(len(columns)):
                row_num += 1
                ws.write(0, col_num, columns[col_num], font_style)
                # Sheet body, remaining rows
            count = 0
            font_style = xlwt.XFStyle()
            y = 1
            for row in serialized_asset.data:
                ws.write(
                    count + y,
                    0,
                    str(
                        row["first_name"]
                        if not None
                        else "" + " " + row["last_name"]
                        if not None
                        else ""
                    ),
                    font_style,
                )
                ws.write(count + y, 1, str(row["username"]), font_style)
                ws.write(count + y, 2, str(row["email"]), font_style)
                ws.write(count + y, 3, str(row["created_at"]), font_style)
                ws.write(count + y, 4, str(row["is_active"]), font_style)

                y = y + 1
            count += 1
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=export_name + ".xls"
            )
        except Exception as e:
            print("USER EXCEL EXPORT EXCEPTION", e)

    def export_region_data(self, serialized_asset, columns, export_name):
        try:
            buffer = io.BytesIO()
            wb = xlwt.Workbook(encoding="utf-8")
            ws = wb.add_sheet(export_name)
            # Sheet header, first row
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num = 0
            for col_num in range(len(columns)):
                row_num += 1
                ws.write(0, col_num, columns[col_num], font_style)
                # Sheet body, remaining rows
            count = 0
            font_style = xlwt.XFStyle()
            y = 1
            for row in serialized_asset.data:
                ws.write(count + y, 0, str(row["name"]), font_style)
                ws.write(count + y, 1, str(row["code"]), font_style)
                ws.write(count + y, 2, str(row["country"]['name']), font_style)
                y = y + 1
            count += 1
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=export_name + ".xls"
            )
        except Exception as e:
            print("REGION EXCEL EXPORT EXCEPTION", e)

    def export_grade_data(self, serialized_asset, columns, export_name):
        try:
            buffer = io.BytesIO()
            wb = xlwt.Workbook(encoding="utf-8")
            ws = wb.add_sheet(export_name)
            # Sheet header, first row
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num = 0
            for col_num in range(len(columns)):
                row_num += 1
                ws.write(0, col_num, columns[col_num], font_style)
                # Sheet body, remaining rows
            count = 0
            font_style = xlwt.XFStyle()
            y = 1
            for row in serialized_asset.data:
                ws.write(count + y, 0, str(row["prefix"]), font_style)
                ws.write(count + y, 1, str(row["number"]), font_style)
                y = y + 1
            count += 1
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=export_name + ".xls"
            )
        except Exception as e:
            print("GRADE EXCEL EXPORT EXCEPTION", e)

    def export_city_data(self, serialized_asset, columns, export_name):
        try:
            buffer = io.BytesIO()
            wb = xlwt.Workbook(encoding="utf-8")
            ws = wb.add_sheet(export_name)
            # Sheet header, first row
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num = 0
            for col_num in range(len(columns)):
                row_num += 1
                ws.write(0, col_num, columns[col_num], font_style)
                # Sheet body, remaining rows
            count = 0
            font_style = xlwt.XFStyle()
            y = 1
            for row in serialized_asset.data:
                ws.write(count + y, 0, str(row["name"]), font_style)
                ws.write(count + y, 1, str(row["code"]), font_style)
                ws.write(count + y, 2, str(row["region"]["name"]), font_style)
                ws.write(count + y, 3, str(row["region"]["country"]["name"]), font_style)

                y = y + 1
            count += 1
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=export_name + ".xls"
            )
        except Exception as e:
            print("CITY EXCEL EXPORT EXCEPTION", e)

    def export_zone_data(self, serialized_asset, columns, export_name):
        try:
            buffer = io.BytesIO()
            wb = xlwt.Workbook(encoding="utf-8")
            ws = wb.add_sheet(export_name)
            # Sheet header, first row
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num = 0
            for col_num in range(len(columns)):
                row_num += 1
                ws.write(0, col_num, columns[col_num], font_style)
                # Sheet body, remaining rows
            count = 0
            font_style = xlwt.XFStyle()
            y = 1
            for row in serialized_asset.data:
                ws.write(count + y, 0, str(row["name"]), font_style)
                ws.write(count + y, 1, str(row["code"]), font_style)
                ws.write(count + y, 2, str(row["city"]["name"]), font_style)
                ws.write(count + y, 3, str(row["city"]["region"]["name"]), font_style)
                ws.write(count + y, 4, str(row["city"]["region"]["country"]["name"]), font_style)  # country here

                y = y + 1
            count += 1
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=export_name + ".xls"
            )
        except Exception as e:
            print("ZONE EXCEL EXPORT EXCEPTION", e)

    def export_subzone_data(self, serialized_asset, columns, export_name):
        try:
            buffer = io.BytesIO()
            wb = xlwt.Workbook(encoding="utf-8")
            ws = wb.add_sheet(export_name)
            # Sheet header, first row
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num = 0
            for col_num in range(len(columns)):
                row_num += 1
                ws.write(0, col_num, columns[col_num], font_style)
                # Sheet body, remaining rows
            count = 0
            font_style = xlwt.XFStyle()
            y = 1
            for row in serialized_asset.data:
                ws.write(count + y, 0, str(row["name"]), font_style)
                ws.write(count + y, 1, str(row["code"]), font_style)
                ws.write(count + y, 2, str(row["zone"]["name"]), font_style)
                ws.write(count + y, 3, str(row["zone"]["city"]["name"]), font_style)
                # country here
                ws.write(
                    count + y, 4, str(row["zone"]["city"]["region"]["name"]), font_style
                )
                ws.write(
                    count + y, 5, str(row["zone"]["city"]["region"]["country"]["name"]), font_style
                )
                y = y + 1
            count += 1
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=export_name + ".xls"
            )
        except Exception as e:
            print("SUBZONE EXCEL EXPORT EXCEPTION", e)

    def export_product_data(self, serialized_asset, columns, export_name):
        try:
            buffer = io.BytesIO()
            wb = xlwt.Workbook(encoding="utf-8")
            ws = wb.add_sheet(export_name)
            # Sheet header, first row
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num = 0
            for col_num in range(len(columns)):
                row_num += 1
                ws.write(0, col_num, columns[col_num], font_style)
                # Sheet body, remaining rows
            count = 0
            font_style = xlwt.XFStyle()
            y = 1
            for row in serialized_asset.data:
                ws.write(count + y, 0, str(row["name"]), font_style)
                ws.write(count + y, 1, str(row["code"]), font_style)
                ws.write(count + y, 2, str(row["description"]), font_style)
                ws.write(count + y, 3, str(row["category"]), font_style)
                ws.write(count + y, 4, str(row["image"]), font_style)
                ws.write(count + y, 5, str(row["manufacturer"]["name"]), font_style)
                ws.write(count + y, 6, str(row["weight"]), font_style)
                ws.write(count + y, 7, str(row["dimensions"]), font_style)
                ws.write(count + y, 8, str(row["product_type"]["name"]), font_style)
                y = y + 1
            count += 1
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=export_name + ".xls"
            )
        except Exception as e:
            print("PRODUCT EXCEL EXPORT EXCEPTION", e)

    def export_launched_product_data(self, serialized_asset, columns, export_name):
        try:
            buffer = io.BytesIO()
            wb = xlwt.Workbook(encoding="utf-8")
            ws = wb.add_sheet(export_name)
            # Sheet header, first row
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num = 0
            for col_num in range(len(columns)):
                row_num += 1
                ws.write(0, col_num, columns[col_num], font_style)
                # Sheet body, remaining rows
            count = 0
            font_style = xlwt.XFStyle()
            y = 1
            for row in serialized_asset.data:
                ws.write(count + y, 0, str(row["name"]), font_style)
                ws.write(count + y, 1, str(row["code"]), font_style)
                ws.write(count + y, 2, str(row["description"]), font_style)
                ws.write(count + y, 3, str(row["category"]), font_style)
                ws.write(count + y, 4, str(row["image"]), font_style)
                ws.write(count + y, 5, str(row["manufacturer"]["name"]), font_style)
                ws.write(count + y, 6, str(row["weight"]), font_style)
                ws.write(count + y, 7, str(row["dimensions"]), font_style)
                ws.write(count + y, 8, str(row["product_type"]["name"]), font_style)
                ws.write(count + y, 9, str(row["country"]["name"]) if row["country"] else "", font_style)
                ws.write(count + y, 10, str(row["region"]["name"]) if row["region"] else "", font_style)
                ws.write(count + y, 11, str(row["zone"]["name"]) if row["zone"] else "", font_style)
                ws.write(count + y, 12, str(row["city"]["name"]) if row["city"] else "", font_style)
                ws.write(count + y, 13, str(row["subzone"]["name"]) if row["subzone"] else "", font_style)
                ws.write(count + y, 14, str(row["channel"]["name"]) if row["channel"] else "", font_style)

                y = y + 1
            count += 1
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=export_name + ".xls"
            )
        except Exception as e:
            print("LAUNCHED PRODUCT EXCEL EXPORT EXCEPTION", e)

    def export_product_type_data(self, serialized_asset, columns, export_name):
        try:
            buffer = io.BytesIO()
            wb = xlwt.Workbook(encoding="utf-8")
            ws = wb.add_sheet(export_name)
            # Sheet header, first row
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num = 0
            for col_num in range(len(columns)):
                row_num += 1
                ws.write(0, col_num, columns[col_num], font_style)
                # Sheet body, remaining rows
            count = 0
            font_style = xlwt.XFStyle()
            y = 1
            for row in serialized_asset.data:
                ws.write(count + y, 0, str(row["name"]), font_style)
                ws.write(count + y, 1, str(row["code"]), font_style)
                ws.write(count + y, 2, str(row["description"]), font_style)
                y = y + 1
            count += 1
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=export_name + ".xls"
            )
        except Exception as e:
            print("PRODUCT TYPE EXCEL EXPORT EXCEPTION", e)

    def export_brand_data(self, serialized_asset, columns, export_name):
        try:
            buffer = io.BytesIO()
            wb = xlwt.Workbook(encoding="utf-8")
            ws = wb.add_sheet(export_name)
            # Sheet header, first row
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num = 0
            for col_num in range(len(columns)):
                row_num += 1
                ws.write(0, col_num, columns[col_num], font_style)
                # Sheet body, remaining rows
            count = 0
            font_style = xlwt.XFStyle()
            y = 1
            for row in serialized_asset.data:
                ws.write(count + y, 0, str(row["name"]), font_style)
                ws.write(count + y, 1, str(row["code"]), font_style)
                ws.write(count + y, 2, str(row["brand_type"]["name"]), font_style)
                y = y + 1
            count += 1
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=export_name + ".xls"
            )
        except Exception as e:
            print("Brand EXCEL EXPORT EXCEPTION", e)

    def export_brand_type_data(self, serialized_asset, columns, export_name):
        try:
            buffer = io.BytesIO()
            wb = xlwt.Workbook(encoding="utf-8")
            ws = wb.add_sheet(export_name)
            # Sheet header, first row
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num = 0
            for col_num in range(len(columns)):
                row_num += 1
                ws.write(0, col_num, columns[col_num], font_style)
                # Sheet body, remaining rows
            count = 0
            font_style = xlwt.XFStyle()
            y = 1
            for row in serialized_asset.data:
                ws.write(count + y, 0, str(row["name"]), font_style)
                ws.write(count + y, 1, str(row["code"]), font_style)
                ws.write(count + y, 2, str(row["description"]), font_style)
                ws.write(count + y, 3, str([r["name"] for r in row["region"]]), font_style)
                ws.write(count + y, 4, str([r["country"]["name"] for r in row["region"]]), font_style)  # country here

                y = y + 1
            count += 1
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=export_name + ".xls"
            )
        except Exception as e:
            print("Brand Type EXCEL EXPORT EXCEPTION", e)

    def export_warehouse_data(self, serialized_asset, columns, export_name):
        try:
            buffer = io.BytesIO()
            wb = xlwt.Workbook(encoding="utf-8")
            ws = wb.add_sheet(export_name)
            # Sheet header, first row
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num = 0
            for col_num in range(len(columns)):
                row_num += 1
                ws.write(0, col_num, columns[col_num], font_style)
                # Sheet body, remaining rows
            count = 0
            font_style = xlwt.XFStyle()
            y = 1
            for row in serialized_asset.data:
                ws.write(count + y, 0, str(row["name"]), font_style)
                ws.write(count + y, 1, str(row["region"]["country"]["name"]), font_style)  # country here
                ws.write(count + y, 2, str(row["region"]["name"]), font_style)
                ws.write(count + y, 3, str(row["city"]["name"]), font_style)
                ws.write(count + y, 4, str(row["zone"]["name"]), font_style)
                ws.write(count + y, 5, str(row["address"]), font_style)
                ws.write(count + y, 6,
                         str(row["person_in_control"]["first_name"]) if row["person_in_control"][
                             "first_name"] else "" + " " + str(row["person_in_control"]["last_name"]) if
                         row["person_in_control"]["last_name"] else "",
                         font_style)
                ws.write(count + y, 7, str(row["items_capacity"]), font_style)
                ws.write(count + y, 8, str(row["warehouse_square_footage"]), font_style)
                ws.write(count + y, 9, str(len(row["product"])), font_style)
                ws.write(count + y, 10, str(row["storage_types"]), font_style)
                ws.write(count + y, 11, str(row["loading_unloading_info"]), font_style)
                ws.write(count + y, 12, str(row["operating_hours"]), font_style)
                ws.write(count + y, 13, str(row["sap_id"]), font_style)
                ws.write(count + y, 14, str(row["longitude"]), font_style)
                ws.write(count + y, 15, str(row["latitude"]), font_style)
                ws.write(count + y, 16, str(row["additional_information"]), font_style)
                ws.write(count + y, 17, str(row["code"]), font_style)
                ws.write(count + y, 18, str(row["category"]), font_style)

                y = y + 1
            count += 1
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=export_name + ".xls"
            )
        except Exception as e:
            print("WAREHOUSE EXCEL EXPORT EXCEPTION", e)

    def export_plant_data(self, serialized_asset, columns, export_name):
        try:
            buffer = io.BytesIO()
            wb = xlwt.Workbook(encoding="utf-8")
            ws = wb.add_sheet(export_name)
            # Sheet header, first row
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num = 0
            for col_num in range(len(columns)):
                row_num += 1
                ws.write(0, col_num, columns[col_num], font_style)
                # Sheet body, remaining rows
            count = 0
            font_style = xlwt.XFStyle()
            y = 1
            for row in serialized_asset.data:
                ws.write(count + y, 0, str(row["name"]), font_style)
                ws.write(count + y, 1, str(row["region"]["country"]["name"]), font_style)  # country here - not working

                ws.write(count + y, 2, str(row["region"]["name"]), font_style)
                ws.write(count + y, 3, str(row["city"]["name"]), font_style)
                ws.write(count + y, 4, str(row["address"]), font_style)
                ws.write(count + y, 5,
                         str(row["person_in_control"]["first_name"] + " " + row["person_in_control"]["last_name"]),
                         font_style)
                ws.write(count + y, 6, str(row["manufacturing_capacity"]), font_style)
                ws.write(count + y, 7, str(row["storage_capacity"]), font_style)
                ws.write(count + y, 8, str(len(row["product"])), font_style)
                ws.write(count + y, 9, str(row["storage_types"]), font_style)
                ws.write(count + y, 10, str(row["loading_unloading_info"]), font_style)
                ws.write(
                    count + y, 11, str(row["security_control_mechanism"]), font_style
                )
                ws.write(count + y, 12, str(row["operating_hours"]), font_style)
                ws.write(count + y, 13, str(row["sap_id"]), font_style)
                ws.write(count + y, 14, str(row["longitude"]), font_style)
                ws.write(count + y, 15, str(row["latitude"]), font_style)
                ws.write(count + y, 16, str(row["additional_information"]), font_style)
                ws.write(count + y, 17, str(row["code"]), font_style)
                y = y + 1
            count += 1
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=export_name + ".xls"
            )
        except Exception as e:
            print("PLANT EXCEL EXPORT EXCEPTION", e)

    def export_outlet_data(self, serialized_asset, columns, export_name):
        try:
            buffer = io.BytesIO()
            wb = xlwt.Workbook(encoding="utf-8")
            ws = wb.add_sheet(export_name)
            # Sheet header, first row
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num = 0
            for col_num in range(len(columns)):
                row_num += 1
                ws.write(0, col_num, columns[col_num], font_style)
                # Sheet body, remaining rows
            count = 0
            font_style = xlwt.XFStyle()
            y = 1
            for row in serialized_asset.data:
                ws.write(count + y, 0, str(row["sap_code"]), font_style)
                ws.write(count + y, 1, str(row["name"]), font_style)
                ws.write(count + y, 2, str(row["ntn"]), font_style)
                ws.write(count + y, 3, str(row["strn"]), font_style)
                ws.write(count + y, 4, str(row["address"]), font_style)
                ws.write(count + y, 5, str(row["owner_name"]), font_style)
                ws.write(count + y, 6, str(row["owner_cnic"]), font_style)
                ws.write(count + y, 7, str(row["email"]), font_style)
                ws.write(count + y, 8, str(row["owner_contact"]), font_style)
                ws.write(count + y, 9, str(row["longitude"]), font_style)
                ws.write(count + y, 10, str(row["latitude"]), font_style)
                ws.write(count + y, 11, str(row["category"]), font_style)
                ws.write(count + y, 12, str(row["region"]["country"]["name"]), font_style)  # country here
                ws.write(count + y, 13, str(row["region"]["name"]), font_style)
                ws.write(count + y, 14, str(row["city"]["name"]), font_style)
                ws.write(count + y, 15, str(row["zone"]["name"]), font_style)
                ws.write(count + y, 16, str(row["sub_zone"]["name"]), font_style)
                ws.write(count + y, 17, str(row["channel"]["name"]), font_style)
                ws.write(
                    count + y,
                    18,
                    str("Allowed" if row["allow_login"] is True else "Not Allowed"),
                    font_style,
                )
                y = y + 1
            count += 1
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=export_name + ".xls"
            )
        except Exception as e:
            print("OUTLET EXCEL EXPORT EXCEPTION", e)

    def export_channel_data(self, serialized_asset, columns, export_name):
        try:
            buffer = io.BytesIO()
            wb = xlwt.Workbook(encoding="utf-8")
            ws = wb.add_sheet(export_name)
            # Sheet header, first row
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num = 0
            for col_num in range(len(columns)):
                row_num += 1
                ws.write(0, col_num, columns[col_num], font_style)
                # Sheet body, remaining rows
            count = 0
            font_style = xlwt.XFStyle()
            y = 1
            for row in serialized_asset.data:
                ws.write(count + y, 0, str(row["name"]), font_style)
                ws.write(count + y, 1, str(row["code"]), font_style)
                ws.write(count + y, 2, str(row["created_at"]), font_style)
                y = y + 1
            count += 1
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=export_name + ".xls"
            )
        except Exception as e:
            print("CHANNEL EXCEL EXPORT EXCEPTION", e)

    def export_country_data(self, serialized_asset, columns, export_name):
        try:
            buffer = io.BytesIO()
            wb = xlwt.Workbook(encoding="utf-8")
            ws = wb.add_sheet(export_name)
            # Sheet header, first row
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num = 0
            for col_num in range(len(columns)):
                row_num += 1
                ws.write(0, col_num, columns[col_num], font_style)
                # Sheet body, remaining rows
            count = 0
            font_style = xlwt.XFStyle()
            y = 1
            for row in serialized_asset.data:
                ws.write(count + y, 0, str(row["name"]), font_style)
                ws.write(count + y, 1, str(row["code"]), font_style)
                y = y + 1
            count += 1
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=export_name + ".xls"
            )
        except Exception as e:
            print("COUNTRY EXCEL EXPORT EXCEPTION", e)

    def export_notification_data(self, serialized_asset, columns, export_name):
        try:
            buffer = io.BytesIO()
            wb = xlwt.Workbook(encoding="utf-8")
            ws = wb.add_sheet(export_name)
            # Sheet header, first row
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num = 0
            for col_num in range(len(columns)):
                row_num += 1
                ws.write(0, col_num, columns[col_num], font_style)
                # Sheet body, remaining rows
            count = 0
            font_style = xlwt.XFStyle()
            y = 1
            for row in serialized_asset.data:
                ws.write(count + y, 0, str(row["name"]), font_style)
                ws.write(count + y, 1, str(row["subject"]), font_style)
                ws.write(count + y, 2, str(row["body"]), font_style)
                ws.write(count + y, 3, str(row["is_published"]), font_style)
                ws.write(count + y, 4, str(row["recipient_list"]), font_style)
                ws.write(count + y, 5, str(row["recipient_roles"]), font_style)
                ws.write(count + y, 6, str(row["recipient_group"]), font_style)

                # ws.write(count + y, 2, str(row["country"]['name']), font_style)
                y = y + 1
            count += 1
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=export_name + ".xls"
            )
        except Exception as e:
            print("NOTIFICATION EXCEL EXPORT EXCEPTION", e)

    def export_role_data(self, serialized_asset, columns, export_name):
        try:
            buffer = io.BytesIO()
            wb = xlwt.Workbook(encoding="utf-8")
            ws = wb.add_sheet(export_name)
            # Sheet header, first row
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num = 0
            for col_num in range(len(columns)):
                row_num += 1
                ws.write(0, col_num, columns[col_num], font_style)
                # Sheet body, remaining rows
            count = 0
            font_style = xlwt.XFStyle()
            y = 1
            for row in serialized_asset.data:
                permitted_features = [r["feature"]["name"] for r in row["features_list"]]
                ws.write(count + y, 0, str(row["name"]), font_style)
                ws.write(count + y, 1, str(permitted_features), font_style)
                ws.write(count + y, 2, str((row["is_active"])), font_style)
                y = y + 1
            count += 1
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=export_name + ".xls"
            )
        except Exception as e:
            print("ROLE EXCEL EXPORT EXCEPTION", e)
