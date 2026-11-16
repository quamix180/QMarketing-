import unittest

from quamix_cmo.agents import AgentResult, AgentTask, CMOOrchestrator


class StubAgent:
    name = "Marketing Strategist"

    def run(self, task):
        return AgentResult(self.name, task.task_id, "completed", {"objective": task.objective})


class AgentContractTests(unittest.TestCase):
    def test_register_and_run_stub_agent(self):
        orchestrator = CMOOrchestrator()
        orchestrator.register(StubAgent())
        result = orchestrator.run_agent(
            "Marketing Strategist",
            AgentTask("task-1", "camp-1", "QUAMIX", "Prepare campaign strategy"),
        )
        self.assertEqual(result.deliverable["objective"], "Prepare campaign strategy")

    def test_agent_must_be_registered(self):
        with self.assertRaisesRegex(RuntimeError, "not configured"):
            CMOOrchestrator().run_agent(
                "Marketing Strategist",
                AgentTask("task-1", "camp-1", "QUAMIX", "Research"),
            )

    def test_readiness_never_claims_live_ready(self):
        status = CMOOrchestrator().readiness()
        self.assertFalse(status["ready_for_live_operation"])
        self.assertEqual(len(status["missing_agents"]), 7)


if __name__ == "__main__":
    unittest.main()
