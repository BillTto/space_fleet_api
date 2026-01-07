from models import Spaceship, Mission, CrewMember


def demo_classes() -> None:

    ship1 = Spaceship(1, "Apollo", "cargo")
    ship2 = Spaceship(2, "Odyssey", "research")


    crew1 = CrewMember(1, "John Carter", "commander")
    crew2 = CrewMember(2, "Ellen Ripley", "engineer")

    print("Crew members:")
    print(crew1.to_dict())
    print(crew2.to_dict())


    mission1 = Mission(1, "Moon mission", "exploration")
    mission1.add_spaceship(ship1)
    mission1.add_spaceship(ship2)

    print("\nMission spaceships:")

    for s in mission1.spaceships:
        print(s.to_dict())


if __name__ == "__main__":
    demo_classes()
