from enum import StrEnum

SANDBOX_BASE_URL = "https://developer.sandbox.connect.skoda-auto.cz"
PRODUCTION_BASE_URL = "https://developer.connect.skoda-auto.cz"
TEST_BASE_URL = "https://public.test-api.connect.skoda-auto.cz"
BETA_URL = "https://public.api.connect.skoda-auto.cz"


class Endpoints(StrEnum):
    PRODUCTION = "production"
    SANDBOX = "sandbox"
    TEST = "test"
    BETA = "beta"

    @property
    def url(self) -> str:
        return ENDPOINT_URLS[self]


ENDPOINT_URLS = {
    Endpoints.PRODUCTION: PRODUCTION_BASE_URL,
    Endpoints.SANDBOX: SANDBOX_BASE_URL,
    Endpoints.TEST: TEST_BASE_URL,
    Endpoints.BETA: BETA_URL,
}
