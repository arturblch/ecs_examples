from .base import configure_base, MoveProcessor
from entitas import Context, Matcher, Processors

def try_base():
    context = Context()
    entity = context.create_entity()
    configure_base(entity)
    print(entity)

    processors = Processors()
    processors.add(MoveProcessor(context))
    
    processors.initialize()
    processors.activate_reactive_processors()

    running = True
    while running:
        processors.execute()
        processors.cleanup()

        break

    processors.clear_reactive_processors()
    processors.tear_down()  