from itb.research_agent.personas import PERSONAS, persona_prompt
from itb.research_agent.swarm import build_swarm_brief


def test_swarm_has_adversarial_persona_mix():
    slugs = {persona.slug for persona in PERSONAS}
    assert "amplitude_bootstrapper" in slugs
    assert "holographic_geometer" in slugs
    assert "swampland_cartographer" in slugs
    assert "phenomenology_scout" in slugs
    assert "numerical_cartographer" in slugs
    assert "adversarial_referee" in slugs


def test_persona_prompt_specializes_base_prompt():
    prompt = persona_prompt("Base discipline.", PERSONAS[0])
    assert "Base discipline." in prompt
    assert PERSONAS[0].name in prompt
    assert "Priority questions" in prompt


def test_swarm_brief_records_current_mission():
    brief = build_swarm_brief()
    assert "Agent Swarm Research Program" in brief
    assert "Remote compute target" in brief
    assert "Adversarial Referee" in brief
