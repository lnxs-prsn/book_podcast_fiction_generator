# STAGE: Story Stage

Invokes the local Story Generator and Story Validator.

## WHEN TO RUN
After the Spec Gate (12_spec_gate.md) returns APPROVED.

## FLOW
1. Run 14_story_generator.md — pass the approved spec, the intake JSON, and the feature map JSON
2. Write output to `output/acceptance_stories.md`
3. Run 15_story_validator.md — pass the stories document and the approved spec
4. Write output to `output/story_validator_report.md`

## ON FAILURE
If the Story Validator returns STORIES_FAILED:
- Read the failed story IDs and their REQUIRED FIX entries
- Pass the failure context to the Boss (06_boss.md) using the CHALLENGE_ROUTING output format
- The Boss routes back to SPEC_WRITING or FEATURE_MAPPING as appropriate
