#ifndef __PE_CHARACTER_CONTROL_PhysicsManager__
#define __PE_CHARACTER_CONTROL_PhysicsManager__

#include "PrimeEngine/Events/Component.h"
#include "PrimeEngine/Scene/MeshInstance.h"

#include <vector>

namespace PE {
	namespace Components {
		struct PhysicsManager : public PE::Components::Component
		{
			PE_DECLARE_CLASS(PhysicsManager);

			PhysicsManager(PE::GameContext& context, PE::MemoryArena arena, PE::Handle hMyself);

			virtual void addDefaultComponents();

			void updateMovingNode(MovingPhysicsNode* mN);

			Vector3 spheresAndPlane(Vector3 a, Vector3 b, Vector3 c, Vector3 d, Vector3 center, float r);
			bool isPointInsideRectangle(Vector3 a, Vector3 b, Vector3 c, Vector3 point);
			Vector3 getClosestPointOnLineSegment(Vector3 point, Vector3 a, Vector3 b);

			std::vector<StaticPhysicsNode*> m_staticNodes;
			std::vector<MovingPhysicsNode*> m_movingNodes;
		};
	}
}

#endif