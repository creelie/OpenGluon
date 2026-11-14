"""Anaxia command router, with compatibility for the original OpenGluon tools."""

import argparse
import sys


def main(argv=None):
    arguments = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description="Anaxia: discover mathematics, explore claims, verify exact evidence")
    parser.add_argument("command", choices=["radar", "archive", "solve", "verify", "experiment", "propose", "reason", "models", "runtime", "campaign", "challenge", "diophantine", "audit", "doctor", "portfolio", "upstreams", "routes", "certify"])
    if not arguments or arguments[0] in ("-h", "--help"):
        parser.print_help()
        return 0
    command = parser.parse_args(arguments[:1]).command
    if command == "radar":
        from .radar import main as run
        return run(arguments[1:])
    if command in ("solve", "verify"):
        from .lab import main as run
        return run(arguments)
    if command == "experiment":
        from .experiments import main as run
        return run(arguments[1:])
    if command == "propose":
        from .providers import main as run
        return run(arguments[1:])
    if command == "reason":
        from .reasoning import main as run
        return run(arguments[1:])
    if command == "models":
        from .providers import models_main as run
        return run(arguments[1:])
    if command in ("archive", "campaign", "challenge", "diophantine", "audit", "runtime"):
        from importlib import import_module
        module = import_module('.' + {'challenge': 'challenges', 'diophantine': 'number_theory'}.get(command, command), 'anaxia')
        return module.main(arguments[1:])
    from opengluon import legacy_main
    return legacy_main(arguments)
