from pydantic import ConfigDict

from .base_model import BaseModel

#: Type URI RFC 9457 prescribes for problems that carry no meaning beyond the
#: status code. The API uses it for generic errors.
ABOUT_BLANK_TYPE = "about:blank"


class ProblemDetails(BaseModel):
    """Error payload of an ``application/problem+json`` response (RFC 9457).

    The members are all optional: a response only has to carry what it can say,
    and the API answers generic failures with ``about:blank``. Members that this
    library does not know (yet) are kept as extras, so a new member published by
    the API is reachable without a release.
    """

    model_config = ConfigDict(extra="allow")

    type: str = ABOUT_BLANK_TYPE
    title: str | None = None
    status: int | None = None
    detail: str | None = None
    instance: str | None = None

    @property
    def slug(self) -> str | None:
        """Machine-readable name of the problem, e.g. ``rate-limit-exceeded``.

        The problem type URI doubles as a link to its documentation page, so its
        last segment names the condition. ``None`` when there is no name to tell
        the caller: ``about:blank`` carries no meaning beyond the status code.
        """
        slug = self.type.rsplit("/", 1)[-1].strip()
        if not slug or slug == ABOUT_BLANK_TYPE:
            return None
        return slug
