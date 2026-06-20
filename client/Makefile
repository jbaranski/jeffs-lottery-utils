.PHONY: all build test lint deploy

all: lint test build

lint:
	npm run prettier:check

test:
	npx ng test --watch=false --browsers=ChromeHeadlessNoSandbox

build:
	npm run update-csp
	npm run prod:build

# netlify-cli is NOT added as a devDependency -- npx downloads it at deploy time.
deploy: build
	npx netlify-cli deploy --prod --dir=dist/client/browser
