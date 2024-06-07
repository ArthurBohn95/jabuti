# Jabuti

Jabuti is a Python powered, tkinter based, functional blocks editor and executer.

## Glossary

### A

#### Anchor

A point in a ``block`` were links can connect. Can be for inputs or outputs. Can be horizontal (for values) or vertical (for flags).
Can have as many links as necessary, and for inputs they are transformed in a list.

### B

#### Block

A function encased with one anchor for each inputs (parameter) and output (return key-value).
Can be controlled by its ``enabler anchor``, and when run without errors sets its ``runflag anchor`` to True.

#### Builtins (module)

Basic blocks that come with jabuti (batteries included).

### C

#### Core (module)

The logic part of jabuti, can work without any GUI.

#### Config (Block)

A special block with no inputs, basically a dict for outputs. Its state is always enabled.

### E

#### Enabler (Anchor)

A special anchor that controls the execution of its block. If it has no Links it is assumed to be True.

### F

#### Flag (Link)

A special link that only connects Runflags to Enablers. Can be True or False.

### G

#### Group

A collection of blocks that can be enabled/disabled together.

### I

#### Input (Anchor)

A special anchor, holds no value, but can check its connected Output via their Link.

### J

#### Jabuti

In english: 'tortoise', a reptile that lives on land and its carapace resembles blocks.

### L

#### Label

A simple text element attached to Blocks and Anchors.

#### Link

A connection between two anchors, does not carry any state, just lets an input communicate to an output.

### O

#### Output (Anchor)

A special anchor that holds a value that can be requested by an Input via their Link.

### R

#### Runflag (Anchor)

A special anchor that starts False but become True after its block run successfully. Connects only to Enablers.

#### Runsystem

An implementation to run blocks sequentially.
