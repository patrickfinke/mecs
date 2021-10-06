import unittest
from mecs import Scene, CommandBuffer

class ComponentA():
    def __init__(self, a):
        self.a = a

class ComponentB():
    def __init__(self, b):
        self.b = b

class SystemA():
    def update(self, scene, **kwargs):
        for eid, (a,) in scene.filter(ComponentA):
            a.a += 1

    init = update
    destroy = update

class SystemB():
    def update(self, scene, **kwargs):
        for eid, (b,) in scene.filter(ComponentB):
            b.b += 1

    init = update
    destroy = update

class SystemAandB():
    def update(self, scene, **kwargs):
        for ent, (a, b) in scene.filter(ComponentA, ComponentB):
            a.a += 1
            b.b += 1

    init = update
    destroy = update

class SystemAnotB():
    def update(self, scene, **kwargs):
        for ent, (a,) in scene.filter(ComponentA, exclude=(ComponentB,)):
            a.a += 1

    init = update
    destroy = update

class SystemValueError():
    def update(self, scene, **kwargs):
        for ent, (a, b) in scene.filter(ComponentA, ComponentB, exclude=(ComponentB,)):
            a.a += 1
            a.b += 1

    init = update
    destroy = update

class CommandBufferTestCase(unittest.TestCase):
    def setUp(self):
        self.scene = Scene()
        self.componentA = ComponentA(0)
        self.componentB = ComponentB(0)
        self.componentA1 = ComponentA(0)
        self.componentA2 = ComponentA(1)

    def test_new(self):
        with CommandBuffer(self.scene) as buffer:
            eid1 = buffer.new(self.componentA)
            eid2 = buffer.new(self.componentB)

        self.assertEqual(self.scene.get(eid1, ComponentA), self.componentA)
        self.assertEqual(self.scene.get(eid2, ComponentB), self.componentB)

    def test_add(self):
        with CommandBuffer(self.scene) as buffer:
            eid1 = buffer.new()
            eid2 = buffer.new()
            buffer.add(eid1, self.componentA)
            buffer.add(eid2, self.componentB)

        self.assertTrue(self.scene.has(eid1, ComponentA))
        self.assertTrue(self.scene.has(eid2, ComponentB))

    def test_set(self):
        eid = self.scene.new()

        with CommandBuffer(self.scene) as buffer:
            buffer.set(eid, self.componentA1)

        self.assertEqual(self.scene.get(eid, ComponentA), self.componentA1)

        with CommandBuffer(self.scene) as buffer:
            buffer.set(eid, self.componentA2)

        self.assertEqual(self.scene.get(eid, ComponentA), self.componentA2)

    def test_remove(self):
        eid = self.scene.new(self.componentA)
        self.assertTrue(self.scene.has(eid, ComponentA))

        with CommandBuffer(self.scene) as buffer:
            buffer.remove(eid, ComponentA)

        self.assertFalse(self.scene.has(eid, ComponentA))

    def test_free(self):
        eid = self.scene.new(self.componentA, self.componentB)
        self.assertTrue(self.scene.has(eid, ComponentA, ComponentB))

        with CommandBuffer(self.scene) as buffer:
            buffer.free(eid)

        self.assertFalse(self.scene.has(eid, ComponentA))
        self.assertFalse(self.scene.has(eid, ComponentB))

class SceneTestCase(unittest.TestCase):
    def setUp(self):
        self.scene = Scene()
        self.eid = self.scene.new()
        self.eid1 = self.scene.new()
        self.eid2 = self.scene.new()
        self.eid3 = self.scene.new()
        self.componentA = ComponentA(0)
        self.componentB = ComponentB(0)
        self.componentA1 = ComponentA(0)
        self.componentA2 = ComponentA(0)
        self.componentA3 = ComponentA(0)
        self.componentB1 = ComponentB(0)
        self.componentB2 = ComponentB(0)
        self.componentB3 = ComponentB(0)
        self.systemA = SystemA()
        self.systemB = SystemB()
        self.systemAnotB = SystemAnotB()

    def test_new_A(self):
        # new entity id
        used = []
        for _ in range(10):
            eid = self.scene.new()
            self.assertFalse(eid in used)

            used.append(eid)

    def test_new_B(self):
        # adding components
        eid = self.scene.new()
        self.assertFalse(self.scene.has(eid, ComponentA))
        self.assertFalse(self.scene.has(eid, ComponentB))

        eid = self.scene.new(self.componentA)
        self.assertTrue(self.scene.has(eid, ComponentA))
        self.assertFalse(self.scene.has(eid, ComponentB))

        eid = self.scene.new(self.componentA, self.componentB)
        self.assertTrue(self.scene.has(eid, ComponentA))
        self.assertTrue(self.scene.has(eid, ComponentB))

    def test_new_XA(self):
        # ValueError
        self.assertRaises(ValueError, self.scene.new, self.componentB, self.componentA, self.componentA)
        self.assertRaises(ValueError, self.scene.new, self.componentB, self.componentA1, self.componentA2)

    def test_free_A(self):
        # case has components
        self.scene.add(self.eid, self.componentA)
        self.scene.add(self.eid, self.componentB)
        self.assertTrue(self.scene.has(self.eid, ComponentA))
        self.assertTrue(self.scene.has(self.eid, ComponentB))

        result = self.scene.free(self.eid)
        self.assertFalse(self.scene.has(self.eid, ComponentA))
        self.assertFalse(self.scene.has(self.eid, ComponentB))
        self.assertTrue(len(result) == 2)
        self.assertTrue(self.componentA in result)
        self.assertTrue(self.componentB in result)

    def test_free_B(self):
        # case has no components
        self.assertFalse(self.scene.has(self.eid, ComponentA))
        self.assertFalse(self.scene.has(self.eid, ComponentB))

        result = self.scene.free(self.eid)
        self.assertFalse(self.scene.has(self.eid, ComponentA))
        self.assertFalse(self.scene.has(self.eid, ComponentB))
        self.assertTrue(len(result) == 0)

    def test_components_A(self):
        # case has components
        self.scene.add(self.eid, self.componentA)
        self.scene.add(self.eid, self.componentB)
        self.assertTrue(self.scene.has(self.eid, ComponentA))
        self.assertTrue(self.scene.has(self.eid, ComponentB))

        result = self.scene.components(self.eid)
        self.assertTrue(len(result) == 2)
        self.assertTrue(self.componentA in result)
        self.assertTrue(self.componentB in result)

    def test_components_B(self):
        # case has no components
        self.assertFalse(self.scene.has(self.eid, ComponentA))
        self.assertFalse(self.scene.has(self.eid, ComponentB))

        result = self.scene.components(self.eid)
        self.assertTrue(len(result) == 0)

    def test_archetype_A(self):
        # case has components
        self.scene.add(self.eid, self.componentA)
        self.scene.add(self.eid, self.componentB)
        self.assertTrue(self.scene.has(self.eid, ComponentA))
        self.assertTrue(self.scene.has(self.eid, ComponentB))

        result = self.scene.archetype(self.eid)
        self.assertTrue(len(result) == 2)
        self.assertTrue(ComponentA in result)
        self.assertTrue(ComponentB in result)

    def test_archetype_B(self):
        # case has no components
        self.assertFalse(self.scene.has(self.eid, ComponentA))
        self.assertFalse(self.scene.has(self.eid, ComponentB))

        result = self.scene.archetype(self.eid)
        self.assertTrue(len(result) == 0)

    def test_add_A(self):
        # return value, single component
        self.assertEqual(self.scene.add(self.eid, self.componentA), self.componentA)
        self.assertEqual(self.scene.add(self.eid, self.componentB), self.componentB)

    def test_add_B(self):
        # return value, multiple components
        self.assertEqual(self.scene.add(self.eid, self.componentA, self.componentB), [self.componentA, self.componentB])

    def test_add_C(self):
        # influence on Scene.has, single component
        self.assertFalse(self.scene.has(self.eid, ComponentA))

        self.scene.add(self.eid, self.componentA)
        self.assertTrue(self.scene.has(self.eid, ComponentA))

    def test_add_D(self):
        # influence on Scene.has, multiple components
        self.assertFalse(self.scene.has(self.eid, ComponentA))

        self.scene.add(self.eid, self.componentA, self.componentB)
        self.assertTrue(self.scene.has(self.eid, ComponentA, ComponentB))

    def test_add_E(self):
        # influence on Scene.components, single component
        self.assertEqual(self.scene.components(self.eid), ())

        self.scene.add(self.eid, self.componentA)
        self.assertEqual(self.scene.components(self.eid), (self.componentA,))

        self.scene.add(self.eid, self.componentB)
        result = self.scene.components(self.eid)
        self.assertTrue(len(result) == 2)
        self.assertTrue(self.componentA in result)
        self.assertTrue(self.componentB in result)

    def test_add_F(self):
        # influence on Scene.components, multiple components
        self.assertEqual(self.scene.components(self.eid), ())

        self.scene.add(self.eid, self.componentA, self.componentB)
        result = self.scene.components(self.eid)
        self.assertTrue(len(result) == 2)
        self.assertTrue(self.componentA in result)
        self.assertTrue(self.componentB in result)

    def test_add_G(self):
        # influence on Scene.archetype, single component
        self.assertEqual(self.scene.archetype(self.eid), ())

        self.scene.add(self.eid, self.componentA)
        self.assertEqual(self.scene.archetype(self.eid), (ComponentA,))

        self.scene.add(self.eid, self.componentB)
        result = self.scene.archetype(self.eid)
        self.assertTrue(len(result) == 2)
        self.assertTrue(ComponentA in result)
        self.assertTrue(ComponentB in result)

    def test_add_H(self):
        # influence on Scene.archetype, multiple components
        self.assertEqual(self.scene.archetype(self.eid), ())

        self.scene.add(self.eid, self.componentA, self.componentB)
        result = self.scene.archetype(self.eid)
        self.assertTrue(len(result) == 2)
        self.assertTrue(ComponentA in result)
        self.assertTrue(ComponentB in result)

    def test_add_XB(self):
        # ValueError
        self.scene.add(self.eid, self.componentA1)
        self.assertTrue(self.scene.has(self.eid, ComponentA))

        self.assertRaises(ValueError, self.scene.add, self.eid, self.componentA2)
        self.assertRaises(ValueError, self.scene.add, self.eid, self.componentA2, self.componentB1)
        self.assertRaises(ValueError, self.scene.add, self.eid, self.componentB1, self.componentA2)
        self.assertRaises(ValueError, self.scene.add, self.eid, self.componentB1, self.componentB2)
        self.assertRaises(ValueError, self.scene.add, self.eid, self.componentB2, self.componentB1)
        self.assertRaises(ValueError, self.scene.add, self.eid, self.componentB1, self.componentB1)
        self.assertRaises(ValueError, self.scene.add, self.eid)

    def test_set_A(self):
        self.assertFalse(self.scene.has(self.eid, ComponentA, ComponentB))

        # adding
        self.scene.set(self.eid, self.componentA1)
        self.assertTrue(self.scene.has(self.eid, ComponentA))
        self.assertEqual(self.scene.get(self.eid, ComponentA), self.componentA1)
        self.assertFalse(self.scene.has(self.eid, ComponentB))

        # adding and overwriting
        self.scene.set(self.eid, self.componentA2, self.componentB2)
        self.assertTrue(self.scene.has(self.eid, ComponentA, ComponentB))
        self.assertEqual(self.scene.get(self.eid, ComponentA), self.componentA2)
        self.assertEqual(self.scene.get(self.eid, ComponentB), self.componentB2)

    def test_set_XB(self):
        # ValueError
        self.scene.set(self.eid, self.componentA)
        self.assertTrue(self.scene.has(self.eid, ComponentA))

        self.assertRaises(ValueError, self.scene.set, self.eid, self.componentA, self.componentA)
        self.assertRaises(ValueError, self.scene.set, self.eid, self.componentA1, self.componentA2)
        self.assertRaises(ValueError, self.scene.set, self.eid, self.componentB, self.componentB)
        self.assertRaises(ValueError, self.scene.set, self.eid, self.componentB1, self.componentB2)
        self.assertRaises(ValueError, self.scene.set, self.eid, self.componentA1, self.componentA2, self.componentB)
        self.assertRaises(ValueError, self.scene.set, self.eid, self.componentA, self.componentB1, self.componentB2)

    def test_has_A(self):
        # case has no components
        self.assertFalse(self.scene.has(self.eid, ComponentA))
        self.assertFalse(self.scene.has(self.eid, ComponentB))
        self.assertFalse(self.scene.has(self.eid, ComponentA, ComponentB))
        self.assertFalse(self.scene.has(self.eid, ComponentB, ComponentA))

    def test_has_B(self):
        # case has one component
        self.scene.add(self.eid, self.componentA)

        self.assertTrue(self.scene.has(self.eid, ComponentA))
        self.assertFalse(self.scene.has(self.eid, ComponentB))
        self.assertFalse(self.scene.has(self.eid, ComponentA, ComponentB))
        self.assertFalse(self.scene.has(self.eid, ComponentB, ComponentA))

    def test_has_C(self):
        # case has multiple components
        self.scene.add(self.eid, self.componentA)
        self.scene.add(self.eid, self.componentB)

        self.assertTrue(self.scene.has(self.eid, ComponentA))
        self.assertTrue(self.scene.has(self.eid, ComponentB))
        self.assertTrue(self.scene.has(self.eid, ComponentA, ComponentB))
        self.assertTrue(self.scene.has(self.eid, ComponentB, ComponentA))

    def test_has_XB(self):
        # ValueError
        self.assertRaises(ValueError, self.scene.has, self.eid)

        self.scene.add(self.eid, self.componentA)
        self.assertRaises(ValueError, self.scene.has, self.eid)

    def test_collect_A(self):
        # case no components
        self.assertEqual(list(self.scene.collect(self.eid)), [])

        # case one component
        self.scene.add(self.eid, self.componentA)
        self.assertTrue(self.scene.has(self.eid, ComponentA))

        self.assertEqual(list(self.scene.collect(self.eid)), [])
        self.assertEqual(list(self.scene.collect(self.eid, ComponentA)), [self.componentA])

        # case two components
        self.scene.add(self.eid, self.componentB)
        self.assertTrue(self.scene.has(self.eid, ComponentA, ComponentB))

        self.assertEqual(list(self.scene.collect(self.eid)), [])
        self.assertEqual(list(self.scene.collect(self.eid, ComponentA)), [self.componentA])
        self.assertEqual(list(self.scene.collect(self.eid, ComponentB)), [self.componentB])
        self.assertEqual(list(self.scene.collect(self.eid, ComponentA, ComponentB)), [self.componentA, self.componentB])
        self.assertEqual(list(self.scene.collect(self.eid, ComponentB, ComponentA)), [self.componentB, self.componentA])

    def test_collect_XB(self):
        # ValueError, case no components
        self.assertRaises(ValueError, self.scene.collect, self.eid, ComponentA)
        self.assertRaises(ValueError, self.scene.collect, self.eid, ComponentB)
        self.assertRaises(ValueError, self.scene.collect, self.eid, ComponentA, ComponentB)
        self.assertRaises(ValueError, self.scene.collect, self.eid, ComponentB, ComponentA)

        # ValueError, case has components
        self.scene.add(self.eid, self.componentB)
        self.assertTrue(self.scene.has(self.eid, ComponentB))

        self.assertRaises(ValueError, self.scene.collect, self.eid, ComponentA)
        self.assertRaises(ValueError, self.scene.collect, self.eid, ComponentA, ComponentB)
        self.assertRaises(ValueError, self.scene.collect, self.eid, ComponentB, ComponentA)

    def test_get_A(self):
        # case one component
        self.scene.add(self.eid, self.componentA)
        self.assertTrue(self.scene.has(self.eid, ComponentA))

        result = self.scene.get(self.eid, ComponentA)
        self.assertEqual(result, self.componentA)

        # case two components
        self.scene.add(self.eid, self.componentB)
        self.assertTrue(self.scene.has(self.eid, ComponentB))

        resultA = self.scene.get(self.eid, ComponentA)
        resultB = self.scene.get(self.eid, ComponentB)
        self.assertEqual(resultA, self.componentA)
        self.assertEqual(resultB, self.componentB)

    def test_get_XB(self):
        # ValueError
        # case no components
        self.assertRaises(ValueError, self.scene.get, self.eid, ComponentA)

        # case other components
        self.scene.add(self.eid, self.componentB)
        self.assertTrue(self.scene.has(self.eid, ComponentB))

        self.assertRaises(ValueError, self.scene.get, self.eid, ComponentA)

    def test_remove_A(self):
        # return value, single component type
        self.scene.add(self.eid, self.componentA)
        self.assertTrue(self.scene.has(self.eid, ComponentA))

        self.assertEqual(self.scene.remove(self.eid, ComponentA), self.componentA)

    def test_remove_B(self):
        # return value, multiple component types
        self.scene.add(self.eid, self.componentA, self.componentB)
        self.assertTrue(self.scene.has(self.eid, ComponentA, ComponentB))

        self.assertEqual(self.scene.remove(self.eid, ComponentA, ComponentB), [self.componentA, self.componentB])

    def test_remove_C(self):
        # influence on Scene.has, single component types
        self.scene.add(self.eid, self.componentA)
        self.assertTrue(self.scene.has(self.eid, ComponentA))

        self.scene.remove(self.eid, ComponentA)
        self.assertFalse(self.scene.has(self.eid, ComponentA))

    def test_remove_D(self):
        # influence on Scene.has, multiple component types
        self.scene.add(self.eid, self.componentA, self.componentB)
        self.assertTrue(self.scene.has(self.eid, ComponentA, ComponentB))

        self.scene.remove(self.eid, ComponentA, ComponentB)
        self.assertFalse(self.scene.has(self.eid, ComponentA))
        self.assertFalse(self.scene.has(self.eid, ComponentB))

    def test_remove_E(self):
        # influence on Scene.components, single component type
        self.scene.add(self.eid, self.componentA)
        self.scene.add(self.eid, self.componentB)
        result = self.scene.components(self.eid)
        self.assertTrue(len(result) == 2)
        self.assertTrue(self.componentA in result)
        self.assertTrue(self.componentB in result)

        self.scene.remove(self.eid, ComponentA)
        result = self.scene.components(self.eid)
        self.assertEqual(result, (self.componentB,))

        self.scene.remove(self.eid, ComponentB)
        result = self.scene.components(self.eid)
        self.assertEqual(result, ())

    def test_remove_F(self):
        # influence on Scene.components, multiple component types
        self.scene.add(self.eid, self.componentA)
        self.scene.add(self.eid, self.componentB)
        result = self.scene.components(self.eid)
        self.assertTrue(len(result) == 2)
        self.assertTrue(self.componentA in result)
        self.assertTrue(self.componentB in result)

        self.scene.remove(self.eid, ComponentA, ComponentB)
        result = self.scene.components(self.eid)
        self.assertEqual(result, ())

    def test_remove_G(self):
        # influence on Scene.archetype, single component type
        self.scene.add(self.eid, self.componentA)
        self.scene.add(self.eid, self.componentB)
        result = self.scene.archetype(self.eid)
        self.assertTrue(len(result) == 2)
        self.assertTrue(ComponentA in result)
        self.assertTrue(ComponentB in result)

        self.scene.remove(self.eid, ComponentA)
        result = self.scene.archetype(self.eid)
        self.assertEqual(result, (ComponentB,))

        self.scene.remove(self.eid, ComponentB)
        result = self.scene.archetype(self.eid)
        self.assertEqual(result, ())

    def test_remove_H(self):
        # influence on Scene.archetype, multiple component types
        self.scene.add(self.eid, self.componentA)
        self.scene.add(self.eid, self.componentB)
        result = self.scene.archetype(self.eid)
        self.assertTrue(len(result) == 2)
        self.assertTrue(ComponentA in result)
        self.assertTrue(ComponentB in result)

        self.scene.remove(self.eid, ComponentA, ComponentB)
        result = self.scene.archetype(self.eid)
        self.assertEqual(result, ())

    def test_remove_XB(self):
        # ValueError, case no components
        self.assertRaises(ValueError, self.scene.remove, self.eid, ComponentA)
        self.assertRaises(ValueError, self.scene.remove, self.eid, ComponentA, ComponentB)
        self.assertRaises(ValueError, self.scene.remove, self.eid, ComponentB, ComponentA)
        self.assertRaises(ValueError, self.scene.remove, self.eid)

    def test_remove_XC(self):
        # ValueError, case other components
        self.scene.add(self.eid, self.componentB)
        self.assertTrue(self.scene.has(self.eid, ComponentB))

        self.assertRaises(ValueError, self.scene.remove, self.eid, ComponentA)
        self.assertRaises(ValueError, self.scene.remove, self.eid, ComponentA, ComponentB)
        self.assertRaises(ValueError, self.scene.remove, self.eid, ComponentB, ComponentA)
        self.assertRaises(ValueError, self.scene.remove, self.eid)

    def test_select_A(self):
        # case no components
        self.scene.add(self.eid1, self.componentA1)
        self.scene.add(self.eid2, self.componentA2)
        self.scene.add(self.eid3, self.componentA3)

        resulteid = []
        for eid, () in self.scene.select():
            resulteid.append(eid)
        self.assertEqual(set(resulteid), set((self.eid1, self.eid2, self.eid3)))

    def test_select_B(self):
        # case one component
        self.scene.add(self.eid1, self.componentA1)
        self.scene.add(self.eid2, self.componentA2)
        self.scene.add(self.eid3, self.componentA3)

        resulteid = []
        resultcompA = []
        for eid, (compA,) in self.scene.select(ComponentA):
            resulteid.append(eid)
            resultcompA.append(compA)
        self.assertEqual(set(resulteid), set((self.eid1, self.eid2, self.eid3)))
        self.assertEqual(set(resultcompA), set((self.componentA1, self.componentA2, self.componentA3)))
        for eid, compA in zip(resulteid, resultcompA):
            self.assertEqual(self.scene.get(eid, ComponentA), compA)

    def test_select_C(self):
        # case two components
        self.scene.add(self.eid1, self.componentA1)
        self.scene.add(self.eid1, self.componentB1)
        self.scene.add(self.eid2, self.componentA2)
        self.scene.add(self.eid2, self.componentB2)
        self.scene.add(self.eid3, self.componentA3)
        self.scene.add(self.eid3, self.componentB3)

        resulteid = []
        resultcompA = []
        resultcompB = []
        for eid, (compA, compB) in self.scene.select(ComponentA, ComponentB):
            resulteid.append(eid)
            resultcompA.append(compA)
            resultcompB.append(compB)
        self.assertEqual(set(resulteid), set((self.eid1, self.eid2, self.eid3)))
        self.assertEqual(set(resultcompA), set((self.componentA1, self.componentA2, self.componentA3)))
        self.assertEqual(set(resultcompB), set((self.componentB1, self.componentB2, self.componentB3)))
        for eid, compA, compB in zip(resulteid, resultcompA, resultcompB):
            self.assertEqual(self.scene.get(eid, ComponentA), compA)
            self.assertEqual(self.scene.get(eid, ComponentB), compB)

    def test_select_D(self):
        # case two components, exclude one
        self.scene.add(self.eid1, self.componentA1)
        self.scene.add(self.eid2, self.componentA2)

        self.scene.add(self.eid3, self.componentA3)
        self.scene.add(self.eid3, self.componentB3)

        resulteid = []
        resultcompA = []
        for eid, (compA,) in self.scene.select(ComponentA, exclude=(ComponentB,)):
            resulteid.append(eid)
            resultcompA.append(compA)
        self.assertEqual(set(resulteid), set((self.eid1, self.eid2)))
        self.assertEqual(set(resultcompA), set((self.componentA1, self.componentA2)))
        for eid, compA in zip(resulteid, resultcompA):
            self.assertEqual(self.scene.get(eid, ComponentA), compA)

    def test_select_XA(self):
        # ValueError
        #self.assertRaises(ValueError, self.scene.filter, ComponentA, ComponentB, exclude=(ComponentA,))
        with self.assertRaises(ValueError):
            next(iter(self.scene.select(ComponentA, ComponentB, exclude=(ComponentA,)))) # use generator to raise exception


if __name__ == "__main__":
    unittest.main()
