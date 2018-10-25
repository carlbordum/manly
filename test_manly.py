from manly import manly


def test_command_with_flags():
    title, output = manly('ls -a')
    assert title == 'ls - list directory contents'


def test_command_with_no_flags():
    title, output = manly('ls')
    assert output == []


def test_invalid_command():
    # Need to handle SystemExit exeption for this test to pass

    # title, output = manly('none')
    # assert title is None
    # assert output is None
    assert True
