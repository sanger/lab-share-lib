import time
from lab_share_lib.rabbit.rabbit_stack import RabbitStack

settings = "config"

if __name__ == "__main__":
    print("Starting LabShare consumer")
    rabbit_stack = RabbitStack(settings)

    rabbit_stack.bring_stack_up()

    try:
        while True:
            if rabbit_stack.is_healthy:
                print("RabbitStack thread is running healthy")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Stopping LabShare consumer...")
