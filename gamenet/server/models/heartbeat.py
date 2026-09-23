from pydantic import BaseModel, Field


class HeartbeatRequest(BaseModel):
    agent_version: str = Field(min_length=1, max_length=50)
    session_id: str | None = Field(default=None, max_length=100)
    pc_state: str = Field(default="ONLINE", pattern="^(ONLINE|READY|BUSY|PAUSED|MAINTENANCE|ERROR|LOCKED)$")


class HeartbeatResponse(BaseModel):
    server_time: str
    pc_id: str
    pc_status: str
    session_id: str | None
    session_status: str | None
    lease_id: str | None
    lease_expires_at: str | None