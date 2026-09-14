// Exercise the actual AutoPlanner adapter for every exported path, without a browser dependency.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
class Element{constructor(tag){this.tag=tag;this.children=[];this.dataset={};this.attributes={};}append(...items){for(const item of items){if(item.tag==='fragment')this.children.push(...item.children);else this.children.push(item);}}replaceChildren(...items){this.children=[];this.append(...items);}setAttribute(k,v){this.attributes[k]=v;}addEventListener(){} }
global.document={createElement:tag=>new Element(tag),createDocumentFragment:()=>new Element('fragment')};
const {build}=require('../assets/route-network.js');require('../assets/autoplanner-tree.js');
const metadata=JSON.parse(fs.readFileSync(path.join(root,'data/database/absynth_metadata.json'),'utf8'));const cache=new Map();let cases=0,steps=0;
for(const [id,info] of Object.entries(metadata.paths)){
 if(!cache.has(info.dataset))cache.set(info.dataset,JSON.parse(fs.readFileSync(path.join(root,info.dataset),'utf8')));
 const data=cache.get(info.dataset),graph=build(data,info);assert.equal(graph.events.length,Object.keys(info.steps).length,id);
 for(const compact of [true,false]){
  const container=new Element('root');const result=AutoPlannerTree.mount(container,graph,{compact,depiction:m=>m.depiction,select:()=>{}});assert.equal(result.renderedSteps,graph.events.length,id);
  const rendered=[];function visit(n){if(n.dataset.node!=null)rendered.push(graph.byId.get(n.dataset.node));n.children.forEach(visit);}visit(container);
  const eventIds=rendered.filter(n=>n.kind==='event').map(n=>n.stepId);assert.equal(new Set(eventIds).size,graph.events.length,id);assert.equal(eventIds.length,graph.events.length,id);
  if(graph.target)assert.equal(rendered[0].id,graph.target.id,id);
 }
 cases++;steps+=graph.events.length;
}
console.log(JSON.stringify({paths:cases,stepOccurrences:steps,modes:2,status:'passed'}));
