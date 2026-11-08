// Isolated server only: inspect real SRP registrations and targeting views.
if (tick === 0) {
 try {
  var R=Java.type('net.minecraft.core.registries.BuiltInRegistries');
  var BB=Java.type('org.kylepitcock.legacyconnector.v1_12_2.bridge.StatesBridge1122');
  var EB=Java.type('org.kylepitcock.legacyconnector.v1_12_2.bridge.EntityBridge1122');
  var world=server.overworld();
  for each(var block in R.BLOCK) {
   var id=String(R.BLOCK.getKey(block));
   if(id.indexOf('srparasites:')===0 && id.indexOf('door')>=0) {
    var legacy=BB.legacyBlock(block.defaultBlockState());
    print('FEEDBACK BLOCK '+id+' class='+legacy.getClass().getName()+' default='+legacy.getDefaultState());
    for(var meta=0;meta<16;meta++) {
     var state=legacy.getStateFromMeta(meta);
     if(BB.toModern(state).getBlock()!==block) print('FEEDBACK WRONG STATE '+id+' meta='+meta+' -> '+BB.toModern(state));
    }
   }
  }
  for each(var type in [Java.type('net.minecraft.world.entity.EntityType').COW,Java.type('net.minecraft.world.entity.EntityType').VILLAGER]) {
   var mob=type.create(world);var view=EB.wrap(mob);
   print('FEEDBACK VIEW '+type+' '+view.getClass().getName()+' alive='+view.isEntityAlive());
  }
  var W=Java.type('org.kylepitcock.legacyconnector.v1_12_2.bridge.WorldBridge1122').wrap(world);
  var fp=Java.type('net.minecraftforge.common.util.FakePlayerFactory').getMinecraft(world);
  var hand=Java.type('net.minecraft.world.InteractionHand').MAIN_HAND;
  var pos=Java.type('net.minecraft.core.BlockPos').containing(0,64,0);
  var ground=Java.type('net.minecraft.world.level.block.Blocks').STONE.defaultBlockState();
  for(var x=-4;x<=12;x++)for(var z=-4;z<=4;z++) world.setBlock(pos.offset(x,-1,z),ground,2);
  var items=Java.type('org.kylepitcock.legacyconnector.v1_12_2.bridge.ItemBridge1122').modItems();
  for each(var it in items) if(String(it.getClass().getName()).indexOf('WeaponMelee')>=0) {
   var mi=Java.type('org.kylepitcock.legacyconnector.v1_12_2.bridge.ItemBridge1122').modern(it,0);
   fp.getInventory().selected=0;fp.setItemInHand(hand,new (Java.type('net.minecraft.world.item.ItemStack'))(mi));
   var lp=EB.wrap(fp), ls=lp.getHeldItemMainhand();
   ls.getOrCreateSubCompound('feedback').setInteger('tick',1);
   fp.getInventory().selected=1;fp.setItemInHand(hand,Java.type('net.minecraft.world.item.ItemStack').EMPTY);
   if(!lp.getHeldItemMainhand().isEmpty())throw new Error('STALE WEAPON IN EMPTY HAND');
   print('FEEDBACK EMPTY HAND PASS');break;
  }
  var save=Java.type('com.dhanantry.scapeandrunparasites.world.SRPSaveData').get(W,50);
  save.setEvolutionPhase(0,8,true,W);save.setGeneration(5,0);
  for each(var type in R.ENTITY_TYPE) {
   var eid=String(R.ENTITY_TYPE.getKey(type));
   if(eid==='srparasites:beckon_siv' || eid==='srparasites:anc_dreadnaut' || eid==='srparasites:ada_longarms') {
    var e=type.create(world);e.setPos(0,64,0);world.addFreshEntity(e);
    print('FEEDBACK HOST '+eid+' parts='+e.getParts().length);feedbackHost=e;
    if(e instanceof Java.type('net.minecraft.world.entity.Mob'))e.finalizeSpawn(world,world.getCurrentDifficultyAt(pos),Java.type('net.minecraft.world.entity.MobSpawnType').COMMAND,null,null);
    var le=EB.wrap(e);print('FEEDBACK GOALS '+eid+' '+le.targetTasks.taskEntries);
    for each(var vt in [Java.type('net.minecraft.world.entity.EntityType').COW,Java.type('net.minecraft.world.entity.EntityType').VILLAGER]){
     var victim=vt.create(world);victim.setPos(4,64,0);world.addFreshEntity(victim);
     for each(var entry in le.targetTasks.taskEntries)if(String(entry.action.getClass().getName()).indexOf('NearestAttackableTargetStatus')>=0){
      print('FEEDBACK STATUS '+le.getParasiteStatus()+' range='+le.getEntityAttribute(Java.type('legacyconnector.v1_12_2.net.minecraft.entity.SharedMonsterAttributes').FOLLOW_RANGE).getAttributeValue()); var sf=entry.action.getClass().getDeclaredField('targetEntitySelector');sf.setAccessible(true);print('FEEDBACK PREDICATE '+sf.get(entry.action).apply(EB.wrap(victim))); var ok=false;for(var attempt=0;attempt<100;attempt++)if(entry.action.shouldExecute()){ok=true;break;}
      print('FEEDBACK TARGET '+vt+' goal='+entry.action.getClass().getName()+' result='+ok);
     }
    }
   }
  }
  print('FEEDBACK INSPECT PASS');
 } catch(e) {print('FEEDBACK INSPECT FAIL '+e);if(e.printStackTrace)e.printStackTrace();}

}

if(tick===40){
 try{ for each(var part in feedbackHost.getParts())print('FEEDBACK PART '+part.getBoundingBox()+' pickable='+part.isPickable()+' alive='+part.legacy.isEntityAlive()); }
 catch(e){print('FEEDBACK PART FAIL '+e);}
 finally{server.halt(false);}
}
