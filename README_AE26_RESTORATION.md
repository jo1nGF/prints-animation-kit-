# Animation Kit — restauração AE 2026

Esta branch contém uma implementação de compatibilidade independente. Os arquivos originais não foram modificados.

## Arquivos necessários

Mantenha na mesma pasta:
- `Animation Kit 26 - Restored Panel.jsx`
- `Text Preset Volume I.jsxinc` (1.333 registros)
- `Text Preset Volume II.jsxinc` (767 registros)

As duas bibliotecas permanecem sem alterações e são carregadas conforme o PACK selecionado. O número do preset é limitado à quantidade do volume ativo. Os sliders IN e OUT permanecem de 0 a 1000.

## Animação

O script cria keyframes lineares no Range Selector Offset:
- IN: varre do valor mínimo ao máximo;
- OUT: varre do máximo ao mínimo;
- as caixas habilitam/desabilitam cada trecho;
- os valores dos sliders são interpretados como milissegundos.

**Nota:** a unidade de IN/OUT foi adotada como milissegundos nesta implementação porque a lógica exata do painel compilado ainda precisa ser confirmada. A restauração do movimento dos seletores é funcionalmente implementada, mas deve ser validada no After Effects 2026 com presets representativos dos dois volumes. O preview do painel é de quadro estático, não playback em tempo real.

## Instalação

1. Baixe o JSX e os dois JSXINC originais deste repositório.
2. Coloque os três arquivos na mesma pasta.
3. Execute o JSX por File > Scripts > Run Script File, ou instale em Scripts/ScriptUI Panels.
4. Selecione uma composição e uma camada de texto antes de aplicar um preset.

## Segurança

Use esta branch separadamente. Não substitua nem apague o JSXBIN/SWF originais.