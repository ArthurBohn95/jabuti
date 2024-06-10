import unittest
import jabuti as jb



class TestConnection(unittest.TestCase):
    def test_minimal(self):
        o1 = jb.Output("o1", int, 42)
        i1 = jb.Input("i1", int)
        l1 = jb.Link(o1, i1)
        
        self.assertEqual(i1.value, 42)
    
    def test_autolink(self):
        o1 = jb.Output("o1", int, 42)
        i1 = jb.Input("i1", int)
        l1 = o1.link_with(i1)
        
        self.assertEqual(i1.value, 42)


class TestBuiltins(unittest.TestCase):
    def test_sum(self):
        o1 = jb.Output("o1", int, 10)
        o2 = jb.Output("o2", float, 32.1)
        o3 = jb.Output("o3", float, -0.1)
        b1 = jb.builtin.BlockSum()
        l1 = jb.Link(o1, b1[">nums"])
        l2 = jb.Link(o2, b1[">nums"])
        l3 = jb.Link(o3, b1[">nums"])
        b1.run()
        self.assertAlmostEqual(b1["<sum"].value, 42.0)
    
    def test_sum2(self):
        c1 = jb.BlockConfig({"x": 10, "y": 32.1, "z": -0.1})
        b1 = jb.builtin.BlockSum()
        l1 = jb.Link(c1["<x"], b1[">nums"])
        l2 = jb.Link(c1["<y"], b1[">nums"])
        l3 = jb.Link(c1["<z"], b1[">nums"])
        b1.run()
        self.assertEqual(b1["<sum"].value, 42.0)
    
    def test_sum3(self):
        c1 = jb.BlockConfig({"x": 10, "y": 32.1, "z": -0.1})
        b1 = jb.builtin.BlockSum()
        l1 = c1["<x"].link_with(b1[">nums"])
        l2 = c1["<y"].link_with(b1[">nums"])
        l3 = c1["<z"].link_with(b1[">nums"])
        l3.unlink()
        del l3
        b1.run()
        self.assertEqual(b1["<sum"].value, 42.1)
    
    def test_flag(self):
        c1 = jb.BlockConfig({"x": 10, "y": 32, "z": 42})
        b1 = jb.builtin.Cmp()
        l1 = c1["<x"].link_with(b1[">x"])
        l2 = c1["<y"].link_with(b1[">y"])
        b1.run()
        
        self.assertTrue(b1['<neq'].value)
        
        b2 = jb.builtin.Abs()
        l3 = b1["<neq"].link_with(b2.enabler)
        l4 = c1["<z"].link_with(b2[">num"])
        b2.run()
        
        self.assertEqual(b2['<neg'].value, -42)



if __name__ == "__main__":
    unittest.main()
