.PHONY: sync-plugins

PLUGINS := jeff-plugin-angular jeff-plugin-project jeff-plugin-python jeff-plugin-tailwind jeff-plugin-typescript

sync-plugins:
	@mkdir -p .claude/agents .claude/skills
	@TMPDIR=$$(mktemp -d) && \
	  trap 'rm -rf "$$TMPDIR"' EXIT && \
	  git clone --quiet --depth=1 https://github.com/jbaranski/jeff-claude.git "$$TMPDIR" && \
	  for plugin in $(PLUGINS); do \
	    src="$$TMPDIR/plugins/$$plugin"; \
	    if [ ! -d "$$src" ]; then echo "Unknown plugin: $$plugin" >&2; exit 1; fi; \
	    for agent in "$$src"/agents/*.md; do \
	      [ -e "$$agent" ] || continue; \
	      cp -L "$$agent" .claude/agents/; \
	    done; \
	    for skill in "$$src"/skills/*; do \
	      [ -e "$$skill" ] || continue; \
	      rm -rf ".claude/skills/$$(basename "$$skill")"; \
	      cp -RL "$$skill" .claude/skills/; \
	    done; \
	  done
	@echo "Synced agents to .claude/agents/ and skills to .claude/skills/"
