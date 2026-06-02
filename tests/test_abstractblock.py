import pyomo.environ as pyo

from paramclass_pyomo import AbstractBlock


def test_pyomo_keyword_rules_build_components():
    class Toy(AbstractBlock):
        x = pyo.Var(initialize=3)
        c = pyo.Constraint(rule=lambda m: m.x >= 1)
        e = pyo.Expression(rule=lambda m: m.x + 1)
        o = pyo.Objective(rule=lambda m: m.e)

    model = pyo.ConcreteModel()
    Toy().build(model)

    assert pyo.value(model.x) == 3
    assert str(model.c.expr) == "1  <=  x"
    assert str(model.e.expr) == "x + 1"
    assert str(model.o.expr) == "e"


def test_pyomo_shorthand_rule_call_still_works():
    class Toy(AbstractBlock):
        x = pyo.Var(initialize=3)
        c = pyo.Constraint()(lambda m: m.x >= 1)

    model = pyo.ConcreteModel()
    Toy().build(model)

    assert str(model.c.expr) == "1  <=  x"


def test_pyomo_initializer_keywords_build_components():
    class Toy(AbstractBlock):
        p = pyo.Param(initialize=7, mutable=True)
        x = pyo.Var(initialize=lambda m: pyo.value(m.p) + 1)

    model = pyo.ConcreteModel()
    Toy().build(model)

    assert pyo.value(model.p) == 7
    assert pyo.value(model.x) == 8
