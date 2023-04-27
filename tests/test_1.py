import pytest
import ans


def to_exec():
    exec(open('ans.py', encoding='utf8').read())

def test_hello(capsys):
    to_exec()
    captured = capsys.readouterr()
    assert captured.out == "Hello World\n"