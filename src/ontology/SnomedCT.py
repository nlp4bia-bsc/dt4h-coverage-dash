import pandas as pd
import numpy as np
import scipy
import matplotlib.pyplot as plt
import networkx as nx
from tqdm import tqdm
import operator



class SnomedCT:

    def __init__(self, file_name_rel, root_concept_code="138875005", relation_types = ["116680003"]) -> None:
        """
            Args:
        file_name_rel (str): Path to the SnomedCT Relationship file in RF2 format
        root_concept_code (str, optional): snomed code of the code from which you want to generate
                                        the ontology file (For example if we want the branch
                                        "Pharmaceutical / biologic product" we would use the code
                                        "373873005", if we want the whole snomed ontology we would
                                        use the code "138875005").Defaults to "138875005".
        relation_types (str, optional): Type of relationship to consider when building the ontology.
                                        Use string "116680003" if you only want to consider "Is a"
                                        relationships, use "all" if you want to consider all types
                                        of relationships (including concept model attributes).Defaults to "116680003".
        self.root_concept_code = root_concept_code
        self.relation_types = relation_types
        self.file_name_rel = file_name_rel
        
        self._load()
        """

        self.file_name_rel = file_name_rel
        self.root_concept_code = root_concept_code
        self.relation_types = relation_types

        self.ontology = self._load_ontology()
        self.rel_active = self._get_active_relations()

    def _load_ontology(self):
        """
        Function to load SnomecCT relationships from RF2 format to netowrkx model.

        Returns:
            Networkx DiGraph: SnomedCT model in a NetworkxDigraph format.
        
        This code is based on the one written by @emreg00 (https://github.com/emreg00/toolbox/blob/master/parse_snomedct.py)
        """
        ontology = nx.MultiDiGraph()
        f = open(self.file_name_rel)
        header = f.readline().strip("\n")
        col_to_idx = dict((val.lower(), i) for i, val in enumerate(header.split("\t")))
        ontology.add_node("138875005")
        for line in f:
            words = line.strip("\n").split("\t")
            #if relation_types == "116680003": #"Is a" relationship code
            
            if (words[col_to_idx["typeid"]] in self.relation_types) & (words[col_to_idx["active"]] == "0"):
                source_id = words[col_to_idx["sourceid"]]
                target_id = words[col_to_idx["destinationid"]]
                try:
                    ontology.remove_edge(target_id, source_id,key=words[col_to_idx["id"]])
                except:
                    print("Removing an already removed relation id {}".format(words[col_to_idx["id"]]))
            elif (words[col_to_idx["typeid"]] in self.relation_types) & (words[col_to_idx["active"]] == "1"):
                source_id = words[col_to_idx["sourceid"]]
                target_id = words[col_to_idx["destinationid"]]
                ontology.add_node(source_id)
                ontology.add_edge(target_id, source_id,key=words[col_to_idx["id"]])
                #print("Add the edge {} - {} key {}".format(target_id, source_id,words[col_to_idx["id"]]))
            
            #else: # All
            #    source_id = words[col_to_idx["sourceid"]]
            #    target_id = words[col_to_idx["destinationid"]]
            #    ontology.add_edge(target_id, source_id)
        #ontology = nx.dfs_tree(ontology, root_concept_code)
        return ontology
    

    def _get_active_relations(self, active_codes_lst=[]):
        """
        Leemos el archivo de relaciones de  snomed línea por línea, borrando aquellas relaciones
        no activas. Posteriormente eliminamos del diccionario resultante las claves (sct codes)
        que hay que borrar por pertenecer a conceptos inactivos. Por último, iteramos para conseguir
        la forma final del diccionario  "CODIGO" --> "Lista de codigos padre".
        """
        file = open(self.file_name_rel, 'r')
        lines = file.readlines()
        rels_dict = dict()
        # First round to get the active relationship
        for index in tqdm(range(0, len(lines))):
            if index == 0:
                continue
            else:  
                elementos = lines[index].split("\t")
                # Si la relación es de tipo is-a
                if (elementos[7] == "116680003"):
                    if elementos[4] in rels_dict.keys():
                    # Si la relaciónIf relation ya ha sido guardado, pero es inactiva, cambiamos estado  
                        if elementos[2] =="1":
                            rels_dict[elementos[4]].append((elementos[5],"1"))
                        else:
                            try:
                            # Si el valor active pasa a 0, borramos el elemento que tenia ese valor
                                rels_dict[elementos[4]].remove((elementos[5],"1"))
                            except:
                                print("WARNING: Trying to remove key {} from dict. The element was removed before".format(elementos[4]))
                    else:
                        if elementos[2] =="1":
                            rels_dict[elementos[4]] = [(elementos[5],"1")] 
                        else: # No guardamos cosas inactivas.
                            continue

        print("Se han obtenido {} relaciones del archivo".format(len(rels_dict)))
        # Una vez hecho, calculamos las claves que hay que eliminar (la diferencia 
        # entre las claves del diccinario y los codigos activs) y las eliminamos
        # del diccionario.
        #keys_to_remove = set(rels_dict.keys()) - set(active_codes_lst)
        #for key in keys_to_remove:
        #    rels_dict.pop(key, None)
        #print("Después de filtrar conceptos no activos quedan {} relaciones".format(len(rels_dict)))
        # Por último, cogemos el primer elemento de cada una d elas listas de los values del dict.
        rels_dict_final = {k: list(map(operator.itemgetter(0), v)) for k, v in rels_dict.items()}
        
        return rels_dict_final
    
    def get_parents(self, code, levels=1):
        """ Funcion recursiva que obtiene una lista de códigos padres de un código dado. 
        Se puede especificar el número de niveles por los que subirá en la ontología para
        obtener los padres.    
        """
        if levels == 0:
            return []
        elif code in self.rel_active:
            parents = []
            for parent in self.rel_active[code]:
                parents += [parent] + self.get_parents(parent, levels - 1)
            return list(np.unique(parents))
        else:
            return []
    
    def get_children(self, code):
        return self.subtree_code_list_with_deep(code, depth_limit=1)
        

    def subtree_code_list_with_deep(self, code, depth_limit):
        """
        Función en la que dado un código y un grafo de NetworkX, devuelve
        la lista de códigos del subarbol que cuelga del código dado. 
        
        Args:
        ontology ([networkx.MultiDigraph]): ontologías calculada
        code ([str]): Código del que se quiere obtener la lista de códigos de su subarbol
        
        Nota: También incluye el código de la entrada (code)
        """
        # Get sucesores
        resultado_dict = nx.dfs_successors(self.ontology, source=code, depth_limit=depth_limit)
        # Cogemos la lista de listas de conceptos 
        lista_smallest_edges = [resultado_dict[i] for i in resultado_dict]
        lista_smallest_edges_flatten = [item for sublist in lista_smallest_edges for item in sublist]
        # Lista de hijos directos
        lista_nodes = list(resultado_dict.keys())
        # Unimos todo
        lista_end = lista_smallest_edges_flatten + lista_nodes
        # Devolmenos una lista de elementos únicos
        return list(set(lista_end))