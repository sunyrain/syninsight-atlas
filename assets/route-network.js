(function(root){
  function build(dataset,info,vertical=false){
    const mols=new Map(dataset.molecules.map(m=>[m.label,m])),sourceSteps=new Map(dataset.steps.map(s=>[s.step_id,s]));
    const nodes=[],edges=[],latest=new Map(),events=[];
    const add=(kind,rank,values)=>{const n={id:String(nodes.length),kind,rank,...values};nodes.push(n);return n;};
    for(const [id,meta] of Object.entries(info.steps)){
      const step=sourceSteps.get(meta.local_step_id);if(!step)throw Error(`Missing recorded step ${meta.local_step_id}`);
      const inputs=step.reactant_labels.map(label=>{if(!latest.has(label))latest.set(label,add('mol',0,{label,molecule:mols.get(label)}));return latest.get(label);});
      const rank=Math.max(0,...inputs.map(n=>n.rank))+1;
      const event=add('event',rank,{stepId:id,step,meta});events.push(event);
      for(const input of inputs)edges.push({from:input.id,to:event.id});
      for(const label of step.product_labels){const product=add('mol',rank+1,{label,molecule:mols.get(label),producedBy:id});latest.set(label,product);edges.push({from:event.id,to:product.id});}
    }
    const byId=new Map(nodes.map(n=>[n.id,n])),incoming=new Map(nodes.map(n=>[n.id,[]])),outgoing=new Map(nodes.map(n=>[n.id,[]]));
    for(const edge of edges){incoming.get(edge.to).push(byId.get(edge.from));outgoing.get(edge.from).push(byId.get(edge.to));}
    for(const n of nodes){if(n.kind==='mol'&&!incoming.get(n.id).length&&outgoing.get(n.id).length)n.rank=Math.min(...outgoing.get(n.id).map(p=>p.rank))-1;}
    const levels=new Map();for(const n of nodes){if(!levels.has(n.rank))levels.set(n.rank,[]);levels.get(n.rank).push(n);}
    for(const rank of [...levels.keys()].sort((a,b)=>a-b)){
      const level=levels.get(rank);
      level.forEach((n,i)=>{const parents=incoming.get(n.id);n.lane=parents.length?parents.reduce((v,p)=>v+p.lane,0)/parents.length:i;});
      level.sort((a,b)=>a.lane-b.lane);
      level.forEach((n,i)=>{if(i)n.lane=Math.max(n.lane,level[i-1].lane+1);});
    }
    const target=latest.get(info.target_label);
    for(const n of nodes){n.target=n===target;n.initial=n.kind==='mol'&&!incoming.get(n.id).length;n.w=n.kind==='mol'?196:94;n.h=n.kind==='mol'?164:46;
      n.x=100+(vertical?n.lane*252:n.rank*172);n.y=100+(vertical?n.rank*136:n.lane*224);
    }
    return {nodes,edges,events,target,byId,incoming,outgoing,vertical,width:Math.max(...nodes.map(n=>n.x+n.w))+100,height:Math.max(...nodes.map(n=>n.y+n.h))+100};
  }
  if(typeof module!=='undefined')module.exports={build};else root.RouteNetwork={build};
})(globalThis);
