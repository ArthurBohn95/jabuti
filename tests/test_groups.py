import unittest
import jabuti as jb



class TestGrouping(unittest.TestCase):
    def test_status(self):
        b1 = jb.builtin.BlockSum("sum")
        b2 = jb.builtin.BlockInv("inv")
        
        g1 = jb.Group([b1, b2], True)
        g1.update(False)
        
        self.assertEqual(b1.enabler.value, False)



if __name__ == "__main__":
    unittest.main()
