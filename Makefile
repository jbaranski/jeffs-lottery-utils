.PHONY: sync-plugins

sync-plugins:
	@mkdir -p .claude/plugins
	@TMPDIR=$$(mktemp -d) && \
	  git clone --depth=1 https://github.com/jbaranski/jeff-claude.git $$TMPDIR && \
	  for plugin in jeff-plugin-angular jeff-plugin-aws-solution-architect jeff-plugin-golang jeff-plugin-project; do \
	    rm -rf .claude/plugins/$$plugin; \
	    cp -rL $$TMPDIR/plugins/$$plugin .claude/plugins/$$plugin 2>/dev/null || true; \
	    for skill_dir in .claude/plugins/$$plugin/skills/*/; do \
	      [ -d "$$skill_dir" ] || continue; \
	      skill=$$(basename $$skill_dir); \
	      if [ ! -f "$${skill_dir}SKILL.md" ] && [ -d "$$TMPDIR/.claude/skills/$$skill" ]; then \
	        rm -rf "$$skill_dir"; \
	        cp -r "$$TMPDIR/.claude/skills/$$skill" ".claude/plugins/$$plugin/skills/"; \
	      fi; \
	    done; \
	  done && \
	  rm -rf $$TMPDIR
	@echo "Plugins synced to .claude/plugins/"
