(function(root){
  // Adapted to source-recorded synthesis operations from AutoPlanner case-2 routeReactionTree.
  function mount(container,graph,{compact,depiction,select}){
    const seen=new Set();container.replaceChildren();
    const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!=null)n.textContent=text;return n;};
    const bind=(element,node)=>{element.dataset.node=node.id;element.setAttribute('aria-label',node.kind==='mol'?`Inspect compound ${node.label}`:`Inspect step ${node.stepId}`);element.addEventListener('click',()=>select(node));return element;};
    function moleculeNode(node,label){
      const m=node.molecule||{},card=bind(el('button',`moleculeNode ${node.target?'target':''}`),node);card.type='button';
      card.append(el('span','nodeFlag',label|| (node.target?'TARGET':node.initial?'STARTING MATERIAL':'CONTINUES')));
      const visual=el('div','moleculeVisual'),inline=el('div','moleculeInline'),img=el('img');img.alt=m.name||`Compound ${node.label}`;img.src=depiction(m);img.draggable=false;img.onerror=()=>{img.replaceWith(el('span','','Structure unavailable'));};inline.append(img);visual.append(inline);
      const smiles=m.canonical_isomeric_smiles||m.canonical_smiles||'Structure not recorded';const text=el('div','nodeText',`${node.label} · ${smiles}`);text.title=smiles;card.append(visual,text);return card;
    }
    function reactionConnector(event){
      let outer=el('div',`reactionConnector ${compact?'compactConnector':''}`);
      const name=event.step.transformation||`Step ${event.stepId}`;outer.title=`Step ${event.stepId}: ${name}`;
      if(compact){outer=bind(outer,event);outer.setAttribute('role','button');outer.tabIndex=0;outer.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();select(event);}});}
      else{const card=bind(el('button','reactionCard'),event);card.type='button';card.append(el('b','reactionFamily',`Step ${event.stepId} · ${name}`));const y=event.meta.yield_percent;card.append(el('span','reactionMeta',y==null||y===''?'Yield not recorded':`${y}% yield`));outer.append(card);}
      return outer;
    }
    function routeReactionTree(event){
      const fragment=document.createDocumentFragment();if(seen.has(event.id))return fragment;seen.add(event.id);fragment.append(reactionConnector(event));
      const precursors=graph.incoming.get(event.id),children=el('div',`routeTreeChildren ${precursors.length>1?'multi':''}`);
      for(const precursor of precursors){const branch=el('div','routeTreeBranch'),producer=graph.incoming.get(precursor.id)[0],shared=producer&&seen.has(producer.id);branch.append(moleculeNode(precursor,shared?'SHARED INTERMEDIATE':producer?'CONTINUES':'STARTING MATERIAL'));
        if(producer&&!shared){const child=el('div','routeChildReaction');child.append(routeReactionTree(producer));branch.append(child);}children.append(branch);
      }
      if(precursors.length)fragment.append(children);return fragment;
    }
    function rootTree(molecule){const tree=el('div','routeTreeRoot');tree.append(moleculeNode(molecule));const producer=graph.incoming.get(molecule.id)[0];if(producer)tree.append(routeReactionTree(producer));return tree;}
    if(graph.target)container.append(rootTree(graph.target));
    const remaining=graph.events.slice().sort((a,b)=>b.rank-a.rank).filter(e=>!seen.has(e.id));
    if(remaining.length){const section=el('section','routeOrphanSection');section.append(el('h4','','Additional recorded modules'),el('p','','These operations have no recorded connection to the target tree.'));
      for(const event of remaining){if(seen.has(event.id))continue;const mod=el('div','routeOrphanModule'),product=graph.outgoing.get(event.id)[0];if(product)mod.append(moleculeNode(product,'MODULE PRODUCT'));mod.append(routeReactionTree(event));section.append(mod);}container.append(section);
    }
    return {renderedSteps:seen.size};
  }
  root.AutoPlannerTree={mount};
})(globalThis);
