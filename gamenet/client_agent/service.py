from threading import Event

from gamenet.client_agent.agent import AgentConfig, ClientAgent


class AgentRuntime:
    """Service-facing runtime; the UI is not required for heartbeat/recovery."""

    def __init__(self, config: AgentConfig) -> None:
        self.stop_event = Event()
        self.agent = ClientAgent(config)

    def run(self) -> None:
        self.agent.run(self.stop_event)

    def stop(self) -> None:
        self.stop_event.set()
        self.agent.close()


def run_windows_service(config: AgentConfig) -> None:
    if __import__("sys").platform != "win32":
        raise RuntimeError("Windows service integration must run on Windows")
    try:
        import servicemanager
        import win32serviceutil
        import win32service
    except ImportError as error:
        raise RuntimeError("pywin32 is required for the Windows service wrapper") from error

    runtime = AgentRuntime(config)

    class GameNetAgentService(win32serviceutil.ServiceFramework):
        _svc_name_ = "GameNetAgent"
        _svc_display_name_ = "GameNet Pro Client Agent"

        def SvcStop(self):
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            runtime.stop()

        def SvcDoRun(self):
            servicemanager.LogInfoMsg("GameNetAgent started")
            runtime.run()

    win32serviceutil.HandleCommandLine(GameNetAgentService)