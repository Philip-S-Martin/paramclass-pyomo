# paramclass-pyomo

`paramclass-pyomo` adapts Pyomo's imperative modeling API to declarative,
class-body model definitions.

It is built on top of [`paramclass`](https://pypi.org/project/paramclass/) and
lets you describe Pyomo components as class attributes, then materialize them
onto a `pyomo.environ.Block` or `ConcreteModel`.

```python
import pyomo.environ as pyo
from paramclass_pyomo import AbstractBlock


class ToyBlock(AbstractBlock):
    x = pyo.Var(initialize=3)
    c = pyo.Constraint(rule=lambda m: m.x >= 1)
    e = pyo.Expression(rule=lambda m: m.x + 1)
    o = pyo.Objective(rule=lambda m: m.e)


model = pyo.ConcreteModel()
ToyBlock().build(model)

assert pyo.value(model.x) == 3
assert str(model.c.expr) == "1  <=  x"
```

The goal is to make reusable Pyomo model pieces easier to package, override,
compose, test, lint, and statically analyze.

## Project Timeline

`paramclass-pyomo` was developed during 2023-2024 and has been used in
production workflows since 2023. Public packaging was added in 2025, and public
documentation was added in 2026 to make the project easier to evaluate, install,
and reuse outside its original environment.

## Install

```bash
pip install paramclass-pyomo
```

For local development alongside `paramclass`:

```bash
uv sync --extra dev
uv run --extra dev pytest
```

The local UV configuration uses `../paramclass` as an editable dependency.

## Why

Pyomo is powerful, but reusable model structure often ends up split across
factory functions, ad hoc builders, and imperative component assignment:

```python
model = pyo.ConcreteModel()
model.capacity = pyo.Param(initialize=100, mutable=True)
model.used = pyo.Var(bounds=(0, None))
model.limit = pyo.Constraint(rule=lambda m: m.used <= m.capacity)
```

That style is natural for Pyomo, but it gives developer tooling less structure
to inspect. Class-based definitions provide a stable surface for code review,
linting, static analysis, generated documentation, and model composition.

`AbstractBlock` keeps Pyomo's component model, while giving each reusable block a
compact Python class definition:

```python
class CapacityBlock(AbstractBlock):
    capacity = pyo.Param(initialize=100, mutable=True)
    used = pyo.Var(bounds=(0, None))
    limit = pyo.Constraint(rule=lambda m: m.used <= m.capacity)
```

Then build it onto a model:

```python
model = pyo.ConcreteModel()
CapacityBlock().build(model)
```

This keeps the imperative construction where Pyomo expects it, while moving the
authoring experience toward a declarative design.

## Examples

### Standard Pyomo Keyword Style

Normal Pyomo keyword construction is supported. Use `rule=` for constraints,
expressions, and objectives, and `initialize=` for parameters and variables.

```python
class ObjectiveBlock(AbstractBlock):
    p = pyo.Param(initialize=7, mutable=True)
    x = pyo.Var(initialize=lambda m: pyo.value(m.p) + 1)
    objective = pyo.Objective(rule=lambda m: m.x)
```

### Shorthand Rule Calls

`paramclass-pyomo` also supports a shorthand callable style for rules:

```python
class ConstraintBlock(AbstractBlock):
    x = pyo.Var(initialize=3)
    c = pyo.Constraint()(lambda m: m.x >= 1)
```

This is optional. The standard Pyomo `rule=` form is usually clearer for public
examples and team code.

### Nested Blocks

`AbstractBlock` instances can be assigned as attributes of other
`AbstractBlock`s. Nested blocks are finalized onto the parent block during
construction.

```python
class Inner(AbstractBlock):
    x = pyo.Var(initialize=1)


class Outer(AbstractBlock):
    inner = Inner()
    cap = pyo.Constraint(rule=lambda m: m.inner.x <= 10)


model = pyo.ConcreteModel()
Outer().build(model)
```

### Indexed Blocks

Pass indexing arguments to the block constructor when defining nested blocks:

```python
class Unit(AbstractBlock):
    x = pyo.Var(initialize=1)


class System(AbstractBlock):
    units = Unit(["a", "b", "c"])
```

When a block is indexed, component construction is applied across each block
data object.

## How It Works

`AbstractBlock` extends `ParamClass` and redirects public attribute assignment to
the underlying Pyomo block. During `build(model)`, deferred class-body
definitions are evaluated and attached to the target model or block.

This lets a Pyomo block definition look declarative to developers and tooling,
while still executing through Pyomo's normal component lifecycle.

Pyomo components that already belong to another block are wrapped with a small
proxy so they can still be referenced safely from generated components.

## Current Limitations

This project intentionally stays close to Pyomo's component model. If a Pyomo
constructor requires keyword arguments such as `rule=` or `initialize=`, prefer
using those explicit keywords in public code.

As with `paramclass`, Python boolean operators such as `and`, `or`, and `not`
are not deferred by the tracing layer.

## Testing

```bash
uv run --extra dev pytest
```
