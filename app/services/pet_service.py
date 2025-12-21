from app.models import db, Pet
from app.services.ai_service import extract_knowledge

def update_pet_growth(pet, content, messages=None):
    """
    根据 AI 回复内容更新宠物成长状态和知识
    """
    is_learned = any(keyword in content for keyword in ["明白了", "学会了", "懂了", "原来是这样"])
    
    if is_learned:
        pet.experience += 20
        pet.owner.coins += 10 # 增加用户金币
        
        # 提取并更新知识
        if messages:
            new_knowledge = extract_knowledge(messages)
            if new_knowledge:
                if pet.knowledge:
                    pet.knowledge += f"\n- {new_knowledge}"
                else:
                    pet.knowledge = f"- {new_knowledge}"
        
        if pet.experience >= pet.level * 100:
            pet.level += 1
            pet.experience = 0
        return True
    return False

def get_or_create_pet(user_id):
    pet = Pet.query.filter_by(user_id=user_id).first()
    if not pet:
        pet = Pet(user_id=user_id)
        db.session.add(pet)
        db.session.commit()
    return pet
