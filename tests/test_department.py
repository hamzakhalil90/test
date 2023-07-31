from tests.fixtures import DjangoClientWithDB


class TestGetDepartmentApi(DjangoClientWithDB):
    def setUp(self):
        super().setUp()

    def test_get_departments_empty_case(self):
        response = self.client.get(
            "/department",
            HTTP_AUTHORIZATION=self.token,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("data").get("data"), [])

    def tearDown(self) -> None:
        super().tearDown()
