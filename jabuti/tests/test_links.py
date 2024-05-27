import unittest
import jabuti as jb

class TestConnection(unittest.TestCase):
    def test_minimal(self):
        o1 = jb.Output("o1", int, 42)
        i1 = jb.Input("i1", int)
        l1 = jb.Link("l1", o1, i1)
        
        self.assertEqual(i1.value, 42)

if __name__ == "__main__":
    unittest.main()
