import unittest

from quamix_cmo.agents import AgentResult, CMOOrchestrator
from quamix_cmo.runtime import AutonomousCMORuntime


class StubAgent:
    def __init__(self, name, status="completed"):
        self.name = name
        self.status = status
        self.tasks = []

    def run(self, task):
        self.tasks.append(task)
        return AgentResult(self.name, task.task_id, self.status, {"agent": self.name})


class RuntimeTests(unittest.TestCase):
    def make_orchestrator(self, stop_agent=None, stop_status="needs_review"):
        orchestrator = CMOOrchestrator()
        agents = []
        for name in orchestrator.REQUIRED_AGENTS:
            status = stop_status if name == stop_agent else "completed"
            agent = StubAgent(name, status)
            agents.append(agent)
            orchestrator.register(agent)
        return orchestrator, agents

    def test_runs_all_agents_in_defined_order_and_passes_context(self):
        orchestrator, agents = self.make_orchestrator()
        report = AutonomousCMORuntime(orchestrator).run_campaign(
            campaign_id="campaign-1", brand_id="QUAMIX", objective="Launch a research campaign"
        )
        self.assertEqual(report.status, "completed")
        self.assertEqual(report.completed_agents, orchestrator.REQUIRED_AGENTS)
        self.assertEqual(len(report.steps), 7)
        self.assertEqual(agents[1].tasks[0].approved_facts[-1]["previous_agent"], agents[0].name)
        self.assertIn("No external publication", agents[0].tasks[0].constraints[1])

    def test_stops_immediately_when_agent_needs_review(self):
        stop = "Content Creation Director"
        orchestrator, agents = self.make_orchestrator(stop)
        report = AutonomousCMORuntime(orchestrator).run_campaign(
            campaign_id="campaign-1", brand_id="QUAMIX", objective="Create a campaign"
        )
        self.assertEqual(report.status, "needs_review")
        self.assertIn(stop, report.stop_reason)
        self.assertEqual(len(report.steps), 2)
        self.assertEqual(agents[2].tasks, [])

    def test_blocks_when_required_agent_is_missing(self):
        orchestrator = CMOOrchestrator()
        report = AutonomousCMORuntime(orchestrator).run_campaign(
            campaign_id="campaign-1", brand_id="QUAMIX", objective="Create a campaign"
        )
        self.assertEqual(report.status, "blocked")
        self.assertIn("Required agents", report.stop_reason)

    def test_rejects_empty_campaign_input(self):
        orchestrator, _ = self.make_orchestrator()
        with self.assertRaises(ValueError):
            AutonomousCMORuntime(orchestrator).run_campaign(
                campaign_id="", brand_id="QUAMIX", objective="Create a campaign"
            )


if __name__ == "__main__":
    unittest.main()
