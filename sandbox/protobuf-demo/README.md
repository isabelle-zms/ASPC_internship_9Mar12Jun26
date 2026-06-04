# Protobuf Demo

This folder contains early experiments with Protocol Buffers.

## Contents
- general-demo → initial idea using small dictionary
- brid-demo → test with actual B-RID JSON sample

## Setup

This project already contains generated protobuf files. Install the protobuf compiler (aka protoc) only if regenerating _pb2.py files

### Dependencies
- Python: 3.10.12
- protobuf: 7.35.0
- protoc: 34.1 (optional)

### Installation

Create virtual environment and activate it (optional)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install protobuf

```bash
pip install protobuf
```

Install protoc (on Linux) (system-wide) (optional)
```bash
apt install -y protobuf-compiler
protoc --version
```

Compile .proto file
```bash
protoc --python_out=. your_proto_file.proto
```

### External Documentation

See full setup instructions or documentations here:
- protobuf: https://pypi.org/project/protobuf/
- protoc: https://protobuf.dev/installation/

## Purpose
Learning and experimentation only.
