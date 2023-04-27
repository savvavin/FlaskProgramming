import pytest
import subprocess


def test_fib1():
    assert subprocess.check_output(['python', 'ans.py'], input=b'1\n').decode().strip() == '1'


def test_fib2():
    assert subprocess.check_output(['python', 'ans.py'], input=b'2\n').decode().strip() == '1'


def test_fib3():
    assert subprocess.check_output(['python', 'ans.py'], input=b'10\n').decode().strip() == '55'
    assert subprocess.check_output(['python', 'ans.py'], input=b'20\n').decode().strip() == '6765'
    assert subprocess.check_output(['python', 'ans.py'], input=b'30\n').decode().strip() == '832040'


def test_input1():
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.check_output(['python', 'ans.py'], input=b'-1\n')


def test_input2():
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.check_output(['python', 'ans.py'], input=b'2.5\n')
        
        
def test_input3():
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.check_output(['python', 'ans.py'], input=b'k\n')
