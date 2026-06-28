# Tower Defense Estocástico — Presentación (HTML)

Deck **HTML estático** con temática *Tower Defense*, para defender el TP de **Simulación de
Sistemas** (Ing. en Informática · UCEMA · Prof. Sergio Sirotinsky). Sin build: se abre en el
navegador y se despliega en **GitHub Pages**.

## Ver
- **Local:** abrir `index.html` en cualquier navegador moderno.
- **Navegación:** `←` `→` o `barra espaciadora` para avanzar · `F` pantalla completa ·
  `P` (o `Ctrl/Cmd+P`) para imprimir / exportar **PDF** (una página por slide).

## Desplegar en GitHub Pages
1. Crear un repo y subir el contenido de esta carpeta (incluido `.nojekyll`).
2. *Settings → Pages →* branch `main`, carpeta `/ (root)` → *Save*.
3. En 1–2 min queda online en `https://<usuario>.github.io/<repo>/`.

> `.nojekyll` evita que GitHub procese el sitio con Jekyll (necesario para servir los assets tal cual).

## Estructura
```
index.html            las 16 slides (1920×1080) + estilos embebidos (tema Tower Defense)
deck-stage.js         web component que escala al viewport, navega y maneja el print-to-PDF
assets/
  frontend_mock.png   mock del reproductor Godot
  dark/*.png          gráficos del backend re-renderizados en tema oscuro neón
make_dark_charts.py   regenera assets/dark/ desde el backend (output.json + experimentos)
.nojekyll             para GitHub Pages
```

## Recorrido (16 slides)
Portada · Mapa (Waves) · **W1** problema + modelo de colas · **W2** variables, PRNG, motor SimPy ·
**W3** validación, rendimiento marginal, óptimo · **W4** experimentos (IC/oleadas/prioridad),
arquitectura, frontend+**demo** · Conclusiones · Cierre.

> Los temas **no** están rotulados por orador (lo recordamos en vivo). Nombres solo en portada y
> cierre, para tener flexibilidad. Hay un cue de **demo en vivo** sobre el propio Tower Defense.

## Editar
- **Texto / slides:** editar `index.html` (cada slide es un `<section>`). Las variables de color y
  tipografía están en `:root` al inicio del `<style>`.
- **Fotos de integrantes:** hoy hay avatares con iniciales (`.member .av`) en portada y cierre.
  Para fotos reales: poner las imágenes en `assets/` y reemplazar el `<div class="av">XX</div>` por
  `<img class="av" src="assets/foto.jpg">` (el `.av` ya recorta en círculo; agregar
  `object-fit:cover` si hace falta).
- **Gráficos:** si cambian las corridas del backend, re-generar con
  `python make_dark_charts.py` (usar el venv del backend) → actualiza `assets/dark/`.

## Datos clave (por si hay que actualizarlos en el texto)
λ=0.40 · μ=0.25 · c=3 · K=10 · ρ=0.533 · c_min=2 · **c\*=3** · Little 1.2% ·
fuga sim 4.0% vs 0.16% analítica · ΔLq=[2.53, 0.25, 0.05, 0.01] · prioridad: Wq fuerte 4.24→2.15 s.

---
Generado con el web component de `deck-stage.js`. QA visual hecho con render headless (Chrome
`--print-to-pdf` → imágenes).
