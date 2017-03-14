import os, sys
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# ShapeAnalysisModule
#

class ShapeAnalysisModule(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Shape Analysis Module"
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["Laura Pascal (Kitware Inc.)"]
    self.parent.helpText = """
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
    """ # replace with organization, grant and thanks.

#
# ShapeAnalysisModuleWidget
#

class ShapeAnalysisModuleWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    #
    #   Global variables
    #
    self.logic = ShapeAnalysisModuleLogic(self)
    self.pipeline = ShapeAnalysisModulePipeline(self)

    #
    #  Interface
    #
    loader = qt.QUiLoader()
    self.moduleName = 'ShapeAnalysisModule'
    scriptedModulesPath = eval('slicer.modules.%s.path' % self.moduleName.lower())
    scriptedModulesPath = os.path.dirname(scriptedModulesPath)
    path = os.path.join(scriptedModulesPath, 'Resources', 'UI', '%s.ui' % self.moduleName)
    qfile = qt.QFile(path)
    qfile.open(qt.QFile.ReadOnly)
    widget = loader.load(qfile, self.parent)
    self.layout = self.parent.layout()
    self.widget = widget
    self.layout.addWidget(widget)

    # Global variables of the Interface
    #   Group Project IO
    self.GroupProjectInputDirectory = self.getWidget('DirectoryButton_GroupProjectInputDirectory')
    self.RandomizeInputs = self.getWidget('checkBox_RandomizeInputs')
    self.GroupProjectOutputDirectory = self.getWidget('DirectoryButton_GroupProjectOutputDirectory')
    self.Debug = self.getWidget('checkBox_Debug')
    #   Post Processed Segmentation
    self.OverwriteSegPostProcess = self.getWidget('checkBox_OverwriteSegPostProcess')
    self.RescaleSegPostProcess = self.getWidget('checkBox_RescaleSegPostProcess')
    self.sx = self.getWidget('SliderWidget_sx')
    self.sy = self.getWidget('SliderWidget_sy')
    self.sz = self.getWidget('SliderWidget_sz')
    self.label_sx = self.getWidget('label_sx')
    self.label_sy = self.getWidget('label_sy')
    self.label_sz = self.getWidget('label_sz')
    self.LabelState = self.getWidget('checkBox_LabelState')
    self.label_ValueLabelNumber = self.getWidget('label_ValueLabelNumber')
    self.ValueLabelNumber = self.getWidget('SliderWidget_ValueLabelNumber')
    #   Generate Mesh Parameters
    self.OverwriteGenParaMesh = self.getWidget('checkBox_OverwriteGenParaMesh')
    self.NumberofIterations = self.getWidget('SliderWidget_NumberofIterations')
    #   Parameters to SPHARM Mesh
    self.OverwriteParaToSPHARMMesh = self.getWidget('checkBox_OverwriteParaToSPHARMMesh')
    self.SubdivLevelValue = self.getWidget('SliderWidget_SubdivLevelValue')
    self.SPHARMDegreeValue = self.getWidget('SliderWidget_SPHARMDegreeValue')
    self.thetaIterationValue = self.getWidget('spinBox_thetaIterationValue')
    self.phiIterationValue = self.getWidget('spinBox_phiIterationValue')
    self.medialMesh = self.getWidget('checkBox_medialMesh')
    #   Visualization
    #   Apply CLIs
    self.applyButton = self.getWidget('applyButton')

    # Connections
    #   Group Project IO
    #   Post Processed Segmentation
    self.RescaleSegPostProcess.connect('clicked(bool)', self.onSelectSpacing)
    self.LabelState.connect('clicked(bool)', self.onSelectValueLabelNumber)
    #   Generate Mesh Parameters
    #   Parameters to SPHARM Mesh
    #   Visualization
    #   Apply CLIs
    self.applyButton.connect('clicked(bool)', self.onApplyButton)


  def cleanup(self):
    pass

  # Functions to recovery the widget in the .ui file
  def getWidget(self, objectName):
    return self.findWidget(self.widget, objectName)

  def findWidget(self, widget, objectName):
    if widget.objectName == objectName:
      return widget
    else:
      for w in widget.children():
        resulting_widget = self.findWidget(w, objectName)
        if resulting_widget:
          return resulting_widget
    return None

  #
  #   Post Processed Segmentation
  #
  def onSelectSpacing(self):
    self.label_sx.enabled = self.RescaleSegPostProcess.checkState()
    self.label_sy.enabled = self.RescaleSegPostProcess.checkState()
    self.label_sz.enabled = self.RescaleSegPostProcess.checkState()
    self.sx.enabled = self.RescaleSegPostProcess.checkState()
    self.sy.enabled = self.RescaleSegPostProcess.checkState()
    self.sz.enabled = self.RescaleSegPostProcess.checkState()

  def onSelectValueLabelNumber(self):
    self.label_ValueLabelNumber.enabled = self.LabelState.checkState()
    self.ValueLabelNumber.enabled = self.LabelState.checkState()

  #
  #   Apply CLIs
  #
  def onApplyButton(self):
    self.pipeline.setup()
    self.pipeline.runCLIModules()

#
# ShapeAnalysisModuleLogic
#

class ShapeAnalysisModuleLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  def __init__(self, interface):
    self.interface = interface

#
# ShapeAnalysisModulePipeline
#
class ShapeAnalysisModulePipeline():
  def __init__(self, interface):
    self.interface = interface

    # Modules
    self.ID = -1
    self.slicerModule = {}  # queue of the modules
    self.moduleParameters = {}
    self.output = {}
    self.output_path = {}
    self.saveOutput = {}

  def setupModule(self, module, cli_parameters, cli_output, cli_path_output, saveOutput):
    self.slicerModule[self.ID] = module
    self.moduleParameters[self.ID] = cli_parameters
    self.output[self.ID] = cli_output
    self.output_path[self.ID] = cli_path_output
    self.saveOutput[self.ID] = saveOutput

  def setup(self):
    # SegPostProcess
    self.ID = 0

    cli_parameters = {}
    inputFilepathList = list()
    inputBasenameList = list()
    inputDirectory = self.interface.GroupProjectInputDirectory.directory.encode('utf-8')
    for file in os.listdir(inputDirectory):
      if file.endswith(".gipl") or file.endswith(".gipl.gz"):
        inputBasenameList.append(file)
        filepath = inputDirectory + '/' + file
        inputFilepathList.append(filepath)
    slicer.util.loadLabelVolume(inputFilepathList[0])
    labelMapVolumeNode_list = slicer.mrmlScene.GetNodesByClass("vtkMRMLLabelMapVolumeNode")
    volume = labelMapVolumeNode_list.GetItemAsObject(0)
    cli_parameters["fileName"] = slicer.mrmlScene.GetNodesByName(volume.GetName()).GetItemAsObject(0)

    output_node = slicer.mrmlScene.AddNode(slicer.vtkMRMLLabelMapVolumeNode())
    output_node.SetName("output_PostProcess")
    cli_parameters["outfileName"] = output_node.GetID()

    if self.interface.RescaleSegPostProcess.checkState():
      cli_parameters["scaleOn"] = True
    cli_parameters["spacing_vect"] = str(self.interface.sx.value) + "," + str(self.interface.sy.value) + "," + str(self.interface.sz.value)
    cli_parameters["label"] = self.interface.ValueLabelNumber.value
    if self.interface.Debug.checkState():
      cli_parameters["debug"] = True

    cli_output = list()
    cli_output.append(output_node)
    cli_output_path = list()
    #    Creation of a folder in the output folder : PostProcess
    outputDirectory = self.interface.GroupProjectOutputDirectory.directory.encode('utf-8')
    pp_outputDirectory = outputDirectory + "/PostProcess"
    if not os.path.exists(pp_outputDirectory):
      os.makedirs(pp_outputDirectory)
    #     Creation of the ouptut filepath for the post process
    output_pp_filepath = pp_outputDirectory + "/" + os.path.splitext(inputBasenameList[0])[0] + "_pp.gipl"
    cli_output_path.append( output_pp_filepath )

    self.setupModule(slicer.modules.segpostprocessclp, cli_parameters, cli_output, cli_output_path, True)

    # GenParaMesh
    self.ID += 1

    cli_parameters = {}
    cli_parameters["infile"] = output_node

    output_para_model = slicer.mrmlScene.AddNode(slicer.vtkMRMLModelNode())
    output_para_model.SetName("output_para")
    cli_parameters["outParaName"] = output_para_model

    output_surfmesh_model = slicer.mrmlScene.AddNode(slicer.vtkMRMLModelNode())
    output_surfmesh_model.SetName("output_surfmesh")
    cli_parameters["outSurfName"] = output_surfmesh_model

    cli_parameters["numIterations"] = self.interface.NumberofIterations.value

    if self.interface.Debug.checkState():
      cli_parameters["debug"] = True

    cli_output = list()
    cli_output.append(output_para_model)
    cli_output.append(output_surfmesh_model)
    cli_output_path = list()
    #    Creation of a folder in the output folder : GenerateMeshParameters
    outputDirectory = self.interface.GroupProjectOutputDirectory.directory.encode('utf-8')
    genparamesh_outputDirectory = outputDirectory + "/GenerateMeshParameters"
    if not os.path.exists(genparamesh_outputDirectory):
      os.makedirs(genparamesh_outputDirectory)
    #     Creation of the ouptut filepath for the post process
    para_output_filepath = genparamesh_outputDirectory + "/" + os.path.splitext(inputBasenameList[0])[0] + "_para.vtk"
    surf_output_filepath = genparamesh_outputDirectory + "/" + os.path.splitext(inputBasenameList[0])[0] + "_surf.vtk"
    cli_output_path.append(para_output_filepath)
    cli_output_path.append(surf_output_filepath)

    self.setupModule(slicer.modules.genparameshclp, cli_parameters, cli_output, cli_output_path, True)

    # ParaToSPHARMMesh
    self.ID += 1

    cli_parameters = {}

    cli_parameters["inParaFile"] = output_para_model

    cli_parameters["inSurfFile"] = output_surfmesh_model

    #    Creation of a folder in the output folder : SPHARMMesh
    outputDirectory = self.interface.GroupProjectOutputDirectory.directory.encode('utf-8')
    SPHARMMesh_outputDirectory = outputDirectory + "/SPHARMMesh"
    if not os.path.exists(SPHARMMesh_outputDirectory):
      os.makedirs(SPHARMMesh_outputDirectory)
    cli_parameters["outbase"] = SPHARMMesh_outputDirectory + "/" + os.path.splitext(inputBasenameList[0])[0]

    cli_parameters["subdivLevel"] = self.interface.SubdivLevelValue.value
    cli_parameters["spharmDegree"] = self.interface.SPHARMDegreeValue.value
    cli_parameters["thetaIteration"] = self.interface.thetaIterationValue.value
    cli_parameters["phiIteration"] = self.interface.phiIterationValue.value
    if self.interface.medialMesh.checkState():
      cli_parameters["medialMesh"] = True
    if self.interface.Debug.checkState():
      cli_parameters["debug"] = True

    cli_output = list()
    cli_output_path = list()

    self.setupModule(slicer.modules.paratospharmmeshclp, cli_parameters, cli_output, cli_output_path, False)

  def runCLI(self):
    slicer.cli.run(self.slicerModule[self.ID], None, self.moduleParameters[self.ID], wait_for_completion=True)

  def saveOutputs(self):
    cli_output = self.output[self.ID]
    cli_output_path = self.output_path[self.ID]
    for i in range(0, len(cli_output)):
      slicer.util.saveNode(cli_output[i], cli_output_path[i])

  def runCLIModules(self):
    for i in range(0, 3):
      self.ID = i
      self.runCLI()
      if self.saveOutput[self.ID]:
        self.saveOutputs()

class ShapeAnalysisModuleTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.delayDisplay(' Tests Passed! ')
