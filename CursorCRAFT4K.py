from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import PerlinNoise
import random

# Initialize Ursina application
app = Ursina()
window.title = 'Minecraft 1.0 Clone'
window.borderless = False
window.fullscreen = False

# Debug message
print_on_screen("Game is running", position=(0, 0), scale=2, duration=5)

# Block types with solid colors
block_types = {
    'grass': color.green,
    'dirt': color.brown,
    'stone': color.gray,
    'wood': color.rgb(139, 69, 19),
    'leaves': color.rgb(0, 100, 0),
    'water': color.blue,
    'sand': color.yellow,
    'end_stone': color.white,
    'obsidian': color.black,
    'bedrock': color.dark_gray,
    'cobblestone': color.rgb(100, 100, 100)
}

# Tools and weapons
tools = {
    'wooden_pickaxe': {'speed': 2, 'suitable_for': ['stone', 'cobblestone']},
    'wooden_axe': {'speed': 2, 'suitable_for': ['wood']},
    'wooden_shovel': {'speed': 2, 'suitable_for': ['dirt', 'grass', 'sand']},
    'wooden_sword': {'speed': 1, 'damage': 4},
}

# Inventory system
inventory = {block: 0 for block in block_types}
inventory.update({tool: 0 for tool in tools})
inventory['wooden_pickaxe'] = 1  # Starting tool
selected_item = 'wooden_pickaxe'

# Terrain parameters
terrain_size = 20
block_size = 1
pnoise = PerlinNoise()

# Player setup
player = FirstPersonController()
player.position = Vec3(0, 25, 0)
player.health = 20
player.experience = 0
player.level = 0

# Sky
sky = Sky(color=color.cyan)

# Dimension flag
in_end_dimension = False

# Mob types
mob_types = {
    'zombie': {'color': color.green, 'attack_type': 'melee', 'damage': 3, 'health': 10},
    'skeleton': {'color': color.white, 'attack_type': 'ranged', 'damage': 2, 'health': 10},
    'enderman': {'color': color.black, 'attack_type': 'melee', 'damage': 4, 'health': 20},
    'ender_dragon': {'color': color.purple, 'attack_type': 'melee', 'damage': 10, 'health': 100},
    'cow': {'color': color.brown, 'attack_type': None, 'damage': 0, 'health': 5}
}

# Function to create a voxel
def create_voxel(position, block_type):
    hardness_values = {
        'grass': 1, 'dirt': 1, 'stone': 3, 'wood': 2, 'leaves': 1,
        'water': 0, 'sand': 1, 'end_stone': 3, 'obsidian': 50, 'bedrock': 100,
        'cobblestone': 3
    }
    voxel = Entity(
        model='cube',
        color=block_types[block_type],
        scale=block_size,
        position=position,
        collider='box'
    )
    voxel.block_type = block_type
    voxel.hardness = hardness_values[block_type]
    voxel.breaking_progress = 0
    return voxel

# Biome generation
def get_biome(x, z):
    biome_noise = PerlinNoise()
    biome_value = biome_noise([x * 0.05, z * 0.05])
    if biome_value < -0.2:
        return 'desert'
    elif biome_value < 0.2:
        return 'plains'
    else:
        return 'forest'

# Generate terrain with biomes and structures
def generate_terrain():
    for x in range(-terrain_size // 2, terrain_size // 2):
        for z in range(-terrain_size // 2, terrain_size // 2):
            biome = get_biome(x, z)
            if biome == 'desert':
                height = int((pnoise([x * 0.1, z * 0.1]) + 1) * 5)
                for y in range(0, height + 1):
                    if y == height:
                        create_voxel(Vec3(x, y, z), 'sand')
                    else:
                        create_voxel(Vec3(x, y, z), 'stone')
            elif biome == 'plains':
                height = int((pnoise([x * 0.1, z * 0.1]) + 1) * 10)
                for y in range(0, height + 1):
                    if y == height:
                        create_voxel(Vec3(x, y, z), 'grass')
                    elif y >= height - 3:
                        create_voxel(Vec3(x, y, z), 'dirt')
                    else:
                        create_voxel(Vec3(x, y, z), 'stone')
                # Simple village house
                if random.random() < 0.01:
                    for dx in range(3):
                        for dz in range(3):
                            create_voxel(Vec3(x + dx, height + 1, z + dz), 'wood')
                            if dx == 0 or dx == 2 or dz == 0 or dz == 2:
                                create_voxel(Vec3(x + dx, height + 2, z + dz), 'cobblestone')
            elif biome == 'forest':
                height = int((pnoise([x * 0.1, z * 0.1]) + 1) * 10)
                for y in range(0, height + 1):
                    if y == height:
                        create_voxel(Vec3(x, y, z), 'grass')
                    elif y >= height - 3:
                        create_voxel(Vec3(x, y, z), 'dirt')
                    else:
                        create_voxel(Vec3(x, y, z), 'stone')
                # Add trees
                if random.random() < 0.1:
                    tree_height = random.randint(3, 5)
                    for ty in range(height + 1, height + 1 + tree_height):
                        create_voxel(Vec3(x, ty, z), 'wood')
                    for lx in range(-1, 2):
                        for lz in range(-1, 2):
                            for ly in range(tree_height - 1, tree_height + 1):
                                create_voxel(Vec3(x + lx, height + 1 + ly, z + lz), 'leaves')

# Generate End dimension terrain
def generate_end_terrain():
    for x in range(-10, 10):
        for z in range(-10, 10):
            if random.random() < 0.1:
                height = random.randint(1, 5)
                for y in range(0, height):
                    create_voxel(Vec3(x, y, z), 'end_stone')
    # End Portal frame
    for x in range(-1, 2):
        for z in range(-1, 2):
            create_voxel(Vec3(x, 0, z), 'obsidian')

# Mob class
class Mob(Entity):
    def __init__(self, position, mob_type):
        super().__init__(
            model='cube',
            color=mob_types[mob_type]['color'],
            scale=1,
            position=position
        )
        self.mob_type = mob_type
        self.health = mob_types[mob_type]['health']
        self.speed = 2 if mob_type != 'ender_dragon' else 4
        self.direction = Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)).normalized()
        self.wander_timer = random.uniform(1, 3)
        self.attack_cooldown = 1
        self.attack_timer = 0
        self.breeding_cooldown = 0

    def update(self):
        if self.mob_type == 'ender_dragon':
            self.position += Vec3(0, 0.1 * sin(time.time()), 0)
            if distance(self, player) < 10 and self.attack_timer <= 0:
                player.health -= mob_types[self.mob_type]['damage']
                self.attack_timer = self.attack_cooldown
            self.attack_timer -= time.dt
        elif self.mob_type == 'enderman':
            if distance(self, player) < 5 and random.random() < 0.01:
                self.position = Vec3(random.uniform(-10, 10), self.position.y, random.uniform(-10, 10))
            elif distance(self, player) < 10:
                direction = (player.position - self.position).normalized()
                self.position += direction * self.speed * time.dt
                if distance(self, player) < 1 and self.attack_timer <= 0:
                    player.health -= mob_types[self.mob_type]['damage']
                    self.attack_timer = self.attack_cooldown
            else:
                self.wander()
        elif self.mob_type in ['zombie', 'skeleton']:
            if distance(self, player) < 10:
                direction = (player.position - self.position).normalized()
                self.position += direction * self.speed * time.dt
                if distance(self, player) < 1 and self.attack_timer <= 0:
                    player.health -= mob_types[self.mob_type]['damage']
                    self.attack_timer = self.attack_cooldown
            else:
                self.wander()
        elif self.mob_type == 'cow':
            self.wander()
            self.breeding_cooldown -= time.dt

        self.attack_timer -= time.dt
        if self.health <= 0:
            destroy(self)
            player.experience += 5

    def wander(self):
        self.wander_timer -= time.dt
        if self.wander_timer <= 0:
            self.direction = Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)).normalized()
            self.wander_timer = random.uniform(1, 3)
        self.position += self.direction * self.speed * time.dt

# Spawn initial mobs
mobs = []
for _ in range(5):
    mob_type = random.choice(['zombie', 'skeleton', 'cow'])
    mob = Mob(position=Vec3(random.uniform(-10, 10), 5, random.uniform(-10, 10)), mob_type=mob_type)
    mobs.append(mob)

# Ender Dragon in End dimension
ender_dragon = None

# Function to enter End dimension
def enter_end_dimension():
    global in_end_dimension, ender_dragon
    if not in_end_dimension:
        in_end_dimension = True
        for entity in scene.entities:
            if isinstance(entity, Entity) and hasattr(entity, 'block_type'):
                destroy(entity)
        generate_end_terrain()
        ender_dragon = Mob(position=Vec3(0, 10, 0), mob_type='ender_dragon')
        mobs.append(ender_dragon)
        player.position = Vec3(0, 5, 0)
        for _ in range(3):
            mob = Mob(position=Vec3(random.uniform(-10, 10), 5, random.uniform(-10, 10)), mob_type='enderman')
            mobs.append(mob)

# Simple enchanting and brewing placeholders
def enchant_item():
    if player.experience >= 10:
        player.experience -= 10
        player.level += 1
        print_on_screen("Item enchanted!", position=(0, 0), scale=2, duration=2)

def brew_potion():
    if inventory['water'] >= 1:
        inventory['water'] -= 1
        print_on_screen("Potion brewed!", position=(0, 0), scale=2, duration=2)

# Handle user input
def input(key):
    global selected_item, in_end_dimension
    if key == '1': selected_item = 'grass'
    elif key == '2': selected_item = 'dirt'
    elif key == '3': selected_item = 'stone'
    elif key == '4': selected_item = 'wood'
    elif key == '5': selected_item = 'leaves'
    elif key == '6': selected_item = 'wooden_pickaxe'
    elif key == '7': selected_item = 'wooden_sword'
    elif key == 'e':  # Enter End dimension
        enter_end_dimension()
    elif key == 'q' and held_keys['left mouse']:  # Enchant
        enchant_item()
    elif key == 'b' and held_keys['left mouse']:  # Brew
        brew_potion()

    # Place block
    if key == 'right mouse down' and inventory[selected_item] > 0:
        hit_info = raycast(camera.position, camera.forward, distance=5)
        if hit_info.hit:
            new_pos = hit_info.entity.position + hit_info.normal
            create_voxel(new_pos, selected_item)
            inventory[selected_item] -= 1

    # Breed animals
    if key == 'f' and selected_item == 'grass':
        for mob in mobs:
            if mob.mob_type == 'cow' and distance(mob, player) < 3 and mob.breeding_cooldown <= 0:
                new_cow = Mob(position=mob.position + Vec3(1, 0, 1), mob_type='cow')
                mobs.append(new_cow)
                mob.breeding_cooldown = 5
                break

# Update game state
def update():
    # Block breaking logic
    if held_keys['left mouse']:
        hit_info = raycast(camera.position, camera.forward, distance=5)
        if hit_info.hit and hasattr(hit_info.entity, 'block_type'):
            voxel = hit_info.entity
            tool_speed = tools.get(selected_item, {'speed': 1})['speed']
            voxel.breaking_progress += tool_speed * time.dt
            if voxel.breaking_progress >= voxel.hardness:
                inventory[voxel.block_type] += 1
                destroy(voxel)

    # Player death and hardcore mode simulation
    if player.health <= 0:
        print_on_screen("You died!", position=(0, 0), scale=2, duration=5)
        player.position = Vec3(0, 25, 0)
        player.health = 20

    # Experience leveling
    if player.experience >= player.level * 10 + 10:
        player.level += 1
        print_on_screen(f"Level up! Level {player.level}", position=(0, 0), scale=2, duration=2)

# Generate terrain and run
generate_terrain()
app
