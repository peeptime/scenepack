# Architecture Standards / 架构规范预留

Version: v0.1

## Layers

ScenePack should keep clear layers:

- capture layer
- lifecycle layer
- analysis layer
- storage layer
- intelligence adapter layer
- UI layer
- export adapter layer

## Lifecycle

Every user-facing flow should map to one of four states:

- `silent_capture`: monitor is observing and can record stable structure without interrupting the user.
- `needs_confirmation`: a scene exists, but ScenePack needs title or intent confirmation before deeper generation.
- `ready_to_handoff`: downstream files exist and can be previewed, copied, dragged, or opened.
- `handed_off`: the user has copied or dragged the context and the package remains traceable.

The UI must show the current lifecycle state. Background actions are allowed only when they keep the user in control.

## Schemas

All saved records should include:

- schema version
- product version
- source
- timestamp
- mode state
- privacy state

Saved data should remain backward compatible through migrations.

## Privacy

Default mode:

- no image upload
- no image content reading
- structure-only capture

AI mode:

- explicit provider
- visible image reading state
- token/cost awareness
- user-configurable key storage

## Logging

Logs should avoid storing image content by default.

Allowed logs:

- capture count
- error code
- schema version
- timing
- mode state

Avoid logs:

- full image path when unnecessary
- API keys
- raw image content
- private user text unless user enables debug export

## Testing

The project should keep:

- unit tests for structure analysis
- package writer tests
- sample layout fixtures
- future Windows capture smoke tests
- future GUI smoke tests

## Git Policy

Recommended:

- small commits
- docs and code kept together for architecture decisions
- no secrets in Git
- ignore local run packages and logs
- tag milestone prototypes
