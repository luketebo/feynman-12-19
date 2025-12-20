from app.models import db, Pet

def update_pet_growth(pet, content):
    """
    根据 AI 回复内容更新宠物成长状态
    """
    is_learned = any(keyword in content for keyword in ["明白了", "学会了", "懂了", "原来是这样"])
    
    if is_learned:
        pet.experience += 20
        pet.coins += 10
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
