# STD-ARCH — Architecture and design standard
Version: 2.0

- **STD-ARCH-1**: Data models, settings and scaling constants live in a dedicated module and carry no control flow. Logic modules import models; they do not define them.
- **STD-ARCH-2**: One shared implementation of any numerically sensitive function (e.g. a slope/threshold characteristic) is used by every consumer (firmware, setting tool, test oracle). Duplicated characteristics are a VIOLATION.
- **STD-ARCH-3**: Layer visibility is declared in the repo contract; a lower layer never imports an upper layer. Cross-layer access goes through the declared interface.
- **STD-ARCH-4**: Every public function states its behaviour for absent, stale and out-of-range inputs. Fail-safe is the default: refuse or hold rather than operate on a guessed value.
- **STD-ARCH-5**: Error handling is part of the design. A refactor that removes a guard, exception path or quality flag must show the equivalent handling elsewhere in the same change.
- **STD-ARCH-6**: Designs map every requirement id to at least one component and one test strategy; unmapped requirements are a design defect, not a documentation gap.
- **STD-ARCH-7**: The architect's review is independent: the reviewer does not edit the design, only returns CONFIRMED or VIOLATION with clause references.
- **STD-ARCH-8**: IEC 61850 model exposure (logical nodes, data objects) is added only for settled behaviour; provisional behaviour is kept internal.
