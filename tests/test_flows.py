import unittest
import jabuti as jb



class TestGrouping(unittest.TestCase):
    def test_lvl3(self):
        pass
    
    def test_lvl4(self):
        #                                                        b4
        #  c1                                                   [¨¨¨¨¨]
        # [¨¨¨¨¨](x1)---<l0>-+        b1          +-<l7>---(num)[ inv ](inv)
        # [     ]             \      [¨¨¨¨¨]     /              [_____]
        # [  c  ](x2)---<l1>---(nums)[ sum ](sum)
        # [  o  ]             /      [_____]     \               b3
        # [  n  ](x3)---<l2>-+          o         +-<l5>---(num)[¨¨¨¨¨]
        # [  f  ]                       | f1                    [ div ](result)
        # [  i  ]                       o         +-<l6>---(div)[_____]
        # [  g  ](y)----<l3>---(num1)[¨¨¨¨¨]     /
        # [     ]                    [ add ](sum)
        # [_____](z)----<l4>---(num2)[_____]
        #                             b2
        c1 = jb.BlockConfig({"x1": 10, "x2": 5, "x3": 60 ,"y": 12, "z": 2})
        
        b1 = jb.builtin.BlockSum()
        l0 = jb.Link(c1["<x1"], b1[">nums"])
        l1 = jb.Link(c1["<x2"], b1[">nums"])
        l2 = jb.Link(c1["<x3"], b1[">nums"])
        
        b2 = jb.builtin.BlockAdd()
        l3 = jb.Link(c1["<y"], b2[">num1"])
        l4 = jb.Link(c1["<z"], b2[">num2"])
        f1 = jb.Link(b1.runflag, b2.enabler)
        
        b3 = jb.builtin.BlockDiv()
        l5 = jb.Link(b1["<sum"], b3[">num"])
        l6 = jb.Link(b2["<sum"], b3[">div"])
        
        b4 = jb.builtin.BlockInv()
        l7 = jb.Link(b1["<sum"], b4[">num"])
        
        b2.run() # is disabled by b1
        b1.run()
        b2.run() # is now enabled by b1
        b3.run()
        b4.run()
        
        self.assertAlmostEqual(b3['<result'].value, 5.3571, 4)
        self.assertEqual(b4['<inv'].value, -75)
    
    def test_lvl4_rs(self):
        #                                                        b4
        #  c1                                                   [¨¨¨¨¨]
        # [¨¨¨¨¨](x1)---<l0>-+        b1          +-<l7>---(num)[ inv ](inv)
        # [     ]             \      [¨¨¨¨¨]     /              [_____]
        # [  c  ](x2)---<l1>---(nums)[ sum ](sum)
        # [  o  ]             /      [_____]     \               b3
        # [  n  ](x3)---<l2>-+          o         +-<l5>---(num)[¨¨¨¨¨]
        # [  f  ]                       | f1                    [ div ](result)
        # [  i  ]                       o         +-<l6>---(div)[_____]
        # [  g  ](y)----<l3>---(num1)[¨¨¨¨¨]     /
        # [     ]                    [ add ](sum)
        # [_____](z)----<l4>---(num2)[_____]
        #                             b2
        c1 = jb.BlockConfig({"x1": 10, "x2": 5, "x3": 60 ,"y": 12, "z": 2})
        
        b1 = jb.builtin.BlockSum()
        l0 = jb.Link(c1["<x1"], b1[">nums"])
        l1 = jb.Link(c1["<x2"], b1[">nums"])
        l2 = jb.Link(c1["<x3"], b1[">nums"])
        
        b2 = jb.builtin.BlockAdd()
        l3 = jb.Link(c1["<y"], b2[">num1"])
        l4 = jb.Link(c1["<z"], b2[">num2"])
        f1 = jb.Link(b1.runflag, b2.enabler)
        
        b3 = jb.builtin.BlockDiv()
        l5 = jb.Link(b1["<sum"], b3[">num"])
        l6 = jb.Link(b2["<sum"], b3[">div"])
        
        b4 = jb.builtin.BlockInv()
        l7 = jb.Link(b1["<sum"], b4[">num"])
        
        runsys = jb.RunSystem()
        for b in [b1, b2, b3, b4]:
            runsys.add_block(b)
        runsys.run_loop()
        
        self.assertAlmostEqual(b3['<result'].value, 5.3571, 4)
        self.assertEqual(b4['<inv'].value, -75)



if __name__ == "__main__":
    unittest.main()
