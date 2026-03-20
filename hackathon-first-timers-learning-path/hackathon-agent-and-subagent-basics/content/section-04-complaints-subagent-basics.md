# Complaints sub-agent basics (15 minutes)

## What a sub-agent is
A sub-agent is a smaller, specialized agent that handles one focused task inside a larger workflow.

In this track, the complaints sub-agent likely exists to:
- receive complaint-related input
- apply complaint-specific instructions
- return a structured answer or action

## Why break work into sub-agents?
- clearer responsibilities
- easier testing
- less prompt confusion
- safer behavior boundaries

## A beginner way to think about it
Main agent:
- receives the overall request
- decides when complaint handling is needed

Complaints sub-agent:
- follows complaint-specific logic
- may format or classify the complaint
- returns results to the main agent

## What to verify when adding a sub-agent
- the sub-agent is called at the right time
- the handoff input is clear
- the output comes back in a form the main agent can use
- edge cases do not silently fail

## Optional video (5-6 minutes)
Watch: **Introduction to Vertex AI Agent Engine**
https://www.youtube.com/watch?v=NrgoZLcY3Kk
