# Interactive Demo

This page demonstrates different ways to add interactivity to your Jupyter Book pages.

## Embedded Content with Iframes

You can embed external content using the `iframe` directive:

:::{iframe} https://www.youtube.com/embed/dQw4w9WgXcQ
:width: 100%
A sample embedded YouTube video
:::

## Executable Code Cell

Using the `code-cell` directive, you can write executable Python code directly in a `.md` file.
When connected to a Binder kernel, users can run and modify these cells:

```{code-cell} python
from betonihu import ConcreteProperties

# Try changing the fck value and re-running!
concrete = ConcreteProperties(fck=30)

print(f"Concrete class: C{concrete.fck:.0f}")
print(f"  Design strength   fcd  = {concrete.fcd:.2f} MPa")
print(f"  Mean strength     fcm  = {concrete.fcm:.1f} MPa")
print(f"  Tensile strength  fctm = {concrete.fctm:.2f} MPa")
print(f"  Elastic modulus   Ecm  = {concrete.Ecm:.2f} GPa")
```

```{code-cell} python
import matplotlib.pyplot as plt

classes = [20, 25, 30, 35, 40, 45, 50]
props = [ConcreteProperties(fck=f) for f in classes]

fig, ax = plt.subplots(figsize=(8, 4))
ax.bar([f"C{p.fck:.0f}" for p in props], [p.fctm for p in props], color="teal")
ax.set_ylabel("fctm [MPa]")
ax.set_title("Mean Tensile Strength by Concrete Class")
plt.tight_layout()
plt.show()
```