from damage.collision import configure_collidable, CollisionProcessor
from damage.damage import DamageByCollisionProcessor
from entitas import Context, Matcher, Processors

def try_base():
    context = Context()
    entity1 = context.create_entity()
    configure_collidable(entity, point)
    print(entity)

    processors = Processors()
    processors.add(CollisionProcessor(context))
    processors.add(DamageByCollisionProcessor(context))
    
    processors.initialize()
    processors.activate_reactive_processors()

    running = True
    while running:
        processors.execute()
        processors.cleanup()

        break

    processors.clear_reactive_processors()
    processors.tear_down()  