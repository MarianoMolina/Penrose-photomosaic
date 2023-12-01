import unittest
# import sys
# import os
# print("Current Working Directory:", os.getcwd())
# print("Python Path:", sys.path)
from ..penrose_tiling import * # python -m photomosaic.unit_tests.test_tiling
class TestPenroseTilingFunctions(unittest.TestCase):
        
    def test_create_initial_triangles(self):
        base = 5
        expected_triangle_count = base * 2
        triangles = create_initial_triangles(base)
        self.assertEqual(len(triangles), expected_triangle_count)
        for triangle in triangles:
            self.assertEqual(triangle[0], "thin")  
                      
    def test_divide_triangles(self):
        base = 5
        divisions = 3
        phi = (5 ** 0.5 + 1) / 2
        initial_triangles = create_initial_triangles(base)
        divided_triangles = divide_triangles(initial_triangles, divisions, phi)
        formula_count = phi * (2 ** divisions) * base * 2
        margin_of_error = 1  # Allow a small margin for approximation errors

        # Check if the actual count is within the margin of error of the formula count
        self.assertTrue(abs(len(divided_triangles) - formula_count) <= margin_of_error)
        
    def test_pair_triangles_and_form_rhombi(self):
        base = 5
        divisions = 1  # Reduced for simplicity
        phi = (5 ** 0.5 + 1) / 2
        initial_triangles = create_initial_triangles(base)
        divided_triangles = divide_triangles(initial_triangles, divisions, phi)
        rhombi = pair_triangles_and_form_rhombi(divided_triangles)
        for rhombus in rhombi:
            self.assertEqual(len(rhombus), 4)
            
    def test_normalize_and_scale_tiles(self):
        # Convert tuples to complex numbers
        rhombi = [(complex(0, 0), complex(1, 0), complex(1, 1), complex(0, 1))]  # A sample square rhombus
        canvas_size = (100, 100)
        scaled_tiles = normalize_and_scale_tiles(rhombi, canvas_size)
        for tile in scaled_tiles:
            # Check if the tile fits within the canvas
            for i in range(0, len(tile), 2):
                self.assertTrue(0 <= tile[i] <= canvas_size[0])
                self.assertTrue(0 <= tile[i+1] <= canvas_size[1])
                                
    def test_find_long_side_and_hash_edge(self):
        v1, v2, v3 = complex(0, 0), complex(12, 0), complex(0, 1)
        long_side = find_long_side(v1, v2, v3)
        self.assertIn(complex(12, 0), long_side)
        self.assertIn(complex(0, 1), long_side)
        hash1 = hash_edge(v1, v2)
        hash2 = hash_edge(v2, v1)  # Should be the same as hash1
        self.assertEqual(hash1, hash2)
        
# Run the tests
if __name__ == '__main__':
    unittest.main()