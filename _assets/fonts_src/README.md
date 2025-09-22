Coloca aquí las fuentes originales (TTF/OTF) antes de subsetting.
Se ignoran en despliegue (no se copian al tema final).

Script principal: `_scratch/subset_fonts.sh`
1. Lee estos archivos TTF/OTF.
2. Genera subsets WOFF2 (latin + símbolos básicos) en `pepecapiro/assets/fonts/<familia>/`.
3. Valida tamaño mínimo (>1KB) y emite warnings si hay sospechosos.

Validación en deploy:
`_scratch/deploy_theme.sh` aborta si detecta woff2 vacíos (hash e3b0...) a menos que se use `--allow-empty-fonts`.

Nombres esperados (ejemplo actual):
	Montserrat-SemiBold.ttf
	Montserrat-Bold.ttf
	OpenSans-Regular.ttf
	OpenSans-SemiBold.ttf
	OpenSans-Italic.ttf

Si cambias los nombres ajusta la matriz `FONTS` dentro de `subset_fonts.sh`.
