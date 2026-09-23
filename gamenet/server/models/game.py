from pydantic import BaseModel, Field


class GameCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(pattern="^[a-z0-9-]+$", max_length=100)
    platform: str = Field(pattern="^(WINDOWS|PS5|OTHER)$")
    launch_type: str = Field(pattern="^(DIRECT_EXE|STEAM|EPIC|RIOT|ZULA|CUSTOM)$")
    executable_path: str | None = None
    working_directory: str | None = None
    launch_arguments: str | None = None
    process_names: list[str] = Field(default_factory=list, max_length=20)


class GameResponse(BaseModel):
    id: str
    name: str
    slug: str
    platform: str
    launch_type: str
    executable_path: str | None
    working_directory: str | None
    launch_arguments: str | None
    process_names: list[str]
    enabled: bool


class LaunchRequest(BaseModel):
    session_id: str = Field(min_length=1)


class LaunchAuthorizationResponse(BaseModel):
    authorized: bool
    game_id: str
    session_id: str
    launch_type: str
    executable_path: str | None
    working_directory: str | None
    launch_arguments: str | None
    process_names: list[str]