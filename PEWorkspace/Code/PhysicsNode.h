#include "PrimeEngine/Math/Vector3.h"
#include "PrimeEngine/Scene/MeshInstance.h" // Assuming this is needed
#include <vector> // Assuming this is needed based on common practice in these files

namespace PE {
	namespace Components {

		// Sphere
		struct MovingPhysicsNode : public PE::Components::Component
		{
			PE_DECLARE_CLASS(MovingPhysicsNode); // creates a static handle and Cinstance<>() methods. still need to create construct

			MovingPhysicsNode(PE::GameContext& context, PE::MemoryArena arena, PE::Handle hMyself);

			virtual void addDefaultComponents();

			Vector3 m_center;
			float m_radius;
		};

		// Box
		struct StaticPhysicsNode : public PE::Components::Component
		{
			PE_DECLARE_CLASS(StaticPhysicsNode); // creates a static handle and Cinstance<>() methods. still need to create construct

			StaticPhysicsNode(PE::GameContext& context, PE::MemoryArena arena, PE::Handle hMyself);

			virtual void addDefaultComponents();

			Vector3 m_boundPoints[8];
			//Vector3 m_a_normal; // Commented out in image
		};
	}
}