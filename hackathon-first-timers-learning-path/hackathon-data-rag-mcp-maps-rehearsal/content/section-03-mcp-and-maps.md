# MCP and Maps basics (15-18 minutes)

## What MCP is
MCP stands for Model Context Protocol. A beginner-friendly description is:

MCP is a standard way for models or agent systems to connect to tools and external services in a more structured way.

## Why this matters for the hackathon
When the track asks you to use MCP with Maps, the core idea is:
- the agent needs access to an external map-related capability
- MCP provides a consistent way to expose that capability

## What Maps usually adds
- place lookup
- geocoding
- route or distance information
- location context for the user request

## Mental model
- the model decides it needs a tool
- the tool server exposes the capability
- the agent sends parameters
- the service returns structured results
- the model uses those results in the response

## Optional videos
Watch: **The Model Context Protocol (MCP)**
https://www.youtube.com/watch?v=CQywdSdi5iA

Watch: **Intro to Google Maps Platform**
https://www.youtube.com/watch?v=kA679ERgBV4
