# Dual Mode Intelligence / 双模式智能架构

Version: v0.1

## Overview

ScenePack should have two modes:

- Mode 1: structural mode
- Mode 2: AI deep understanding mode

Mode 1 must work independently. Mode 2 enhances it.

## Mode 1: Structural Mode

Mode 1 does not read image content.

It can use:

- window position
- image box size
- visible area
- spatial graph
- density
- whitespace
- layout changes
- user typed text if available

It cannot claim:

- this image is a person
- this image is a table
- this image is a website
- this image is a child
- this image is a fight

Those are image-content judgments and belong to Mode 2.

## Mode 1 Output

Mode 1 outputs:

- layout facts
- structure pool hits
- title candidates if possible
- layout message
- inference gates

It does not output final project reasoning.

## Mode 2: AI Deep Understanding Mode

Mode 2 may read image content and user typed text.

It can use:

- user-provided API key
- compatible AI host
- future hosted ScenePack service
- optional local OCR or local model

It can generate:

- content labels
- stronger title candidates
- semantic grouping
- project summary
- task candidates
- naming plan
- downstream context files

## AI Provider Strategy

Best time path:

- keep Mode 1 independent
- support user-provided API keys early
- support external intelligent hosts through adapters
- postpone self-hosted AI until usage and payment are validated

## Token Control

Mode 1 output should not be sent raw to AI.

Before Mode 2, ScenePack should compress:

- many items into regions
- low-value items into pools
- stable items into anchors
- uncertain items into warnings
- pairwise relations into graph summaries

Avoid sending:

- full pairwise relation graphs
- low-confidence relation spam
- redundant coordinate text
- all images by default

## Privacy Rule

Default behavior:

- no image upload
- no image content reading unless enabled
- local structure only

AI behavior:

- user must provide or approve provider
- image reading state must be visible
- token cost should be visible or estimated

## Skills Settings

ScenePack should provide a Skills settings entry.

Users can configure:

- preferred title style
- naming conventions
- project types
- ignored structure signals
- trusted AI providers
- language preference
- personal layout habits
- downstream export targets

