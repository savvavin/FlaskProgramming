import pytest
import subprocess


def test_addition1():
    assert subprocess.check_output(['python', 'ans.py'], input=b'2\n3\n').decode().strip() == '5'


def test_addition2():
    assert subprocess.check_output(['python', 'ans.py'], input=b'-5\n5\n').decode().strip() == '0'


def test_addition3():
    assert subprocess.check_output(['python', 'ans.py'], input=b'100\n-100\n').decode().strip() == '0'


def test_input1():
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.check_output(['python', 'ans.py'], input=b'a\nb\n')


def test_input2():
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.check_output(['python', 'ans.py'], input=b'5\n')
