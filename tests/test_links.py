import unittest
import jabuti as jb



class TestConnection(unittest.TestCase):
    def test_minimal(self):
        o1 = jb.Output("o1", int, 42)
        i1 = jb.Input("i1", int)
        l1 = jb.Link("l1", o1, i1)
        
        self.assertEqual(i1.value, 42)

class TestBuiltins(unittest.TestCase):
    def test_sum(self):
        o1 = jb.Output("o1", int, 10)
        o2 = jb.Output("o2", float, 32.1)
        o3 = jb.Output("o3", float, -0.1)
        b1 = jb.builtin.BlockSum("b1")
        l1 = jb.Link("l1", o1, b1[">nums"])
        l2 = jb.Link("l2", o2, b1[">nums"])
        l3 = jb.Link("l3", o3, b1[">nums"])
        b1.run()
        self.assertAlmostEqual(b1["<sum"].value, 42.0)

if __name__ == "__main__":
    unittest.main()
